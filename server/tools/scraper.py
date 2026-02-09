"""
Web Scraper Tool
Extracts main content from gaming websites
"""
import httpx
from bs4 import BeautifulSoup
import re


# User agent to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# Selectors for common gaming sites
CONTENT_SELECTORS = {
    "fextralife.com": ["div.wiki-content", "div#wiki-content-block", "article"],
    "fandom.com": ["div.mw-parser-output", "div.page-content", "article"],
    "icyveins.com": ["div.page_content", "article.guide_content", "main"],
    "mobafire.com": ["div.guide-content", "div.build-wrapper", "main"],
    "reddit.com": ["div[data-test-id='post-content']", "div.Post", "shreddit-post"],
    "u.gg": ["div.champion-stats", "div.build-content", "main"],
    "default": ["article", "main", "div.content", "div.post-content", "div.entry-content"]
}


async def scrape_gaming_content(url: str, max_length: int = 5000) -> str:
    """
    Scrape and extract main content from a gaming website.
    
    Args:
        url: URL to scrape
        max_length: Maximum characters to return
        
    Returns:
        Extracted text content
    """
    
    try:
        async with httpx.AsyncClient(timeout=7.0, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove script, style, nav elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
                tag.decompose()
            
            # Find the best content selector
            content = None
            
            # Check site-specific selectors
            for domain, selectors in CONTENT_SELECTORS.items():
                if domain in url:
                    for selector in selectors:
                        content = soup.select_one(selector)
                        if content:
                            break
                    break
            
            # Fallback to default selectors
            if not content:
                for selector in CONTENT_SELECTORS["default"]:
                    content = soup.select_one(selector)
                    if content:
                        break
            
            # Last resort: body
            if not content:
                content = soup.body
            
            if not content:
                return ""
            
            # Extract and clean text
            text = content.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)
            
            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error scraping {url}: {e.response.status_code}")
        return ""
    except httpx.TimeoutException:
        print(f"Timeout scraping {url}")
        return ""
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


async def extract_structured_data(url: str) -> dict:
    """
    Extract structured data (tables, lists) from a page.
    Useful for build pages with item lists.
    """
    
    try:
        async with httpx.AsyncClient(timeout=7.0, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            result = {
                "tables": [],
                "lists": [],
                "headings": []
            }
            
            # Extract tables
            for table in soup.find_all("table")[:5]:
                rows = []
                for tr in table.find_all("tr")[:20]:
                    cells = [
                        td.get_text(strip=True) 
                        for td in tr.find_all(["td", "th"])
                    ]
                    if cells:
                        rows.append(cells)
                if rows:
                    result["tables"].append(rows)
            
            # Extract lists
            for ul in soup.find_all(["ul", "ol"])[:10]:
                items = [li.get_text(strip=True) for li in ul.find_all("li")[:15]]
                if items:
                    result["lists"].append(items)
            
            # Extract headings
            for h in soup.find_all(["h1", "h2", "h3"])[:15]:
                result["headings"].append(h.get_text(strip=True))
            
            return result
            
    except Exception as e:
        print(f"Error extracting structured data from {url}: {e}")
        return {"tables": [], "lists": [], "headings": []}
