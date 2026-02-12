import sys
from duckduckgo_search import DDGS
import inspect

with open("debug_news.txt", "w", encoding="utf-8") as f:
    try:
        f.write(f"DDGS.news signature: {inspect.signature(DDGS.news)}\n")
    except Exception as e:
        f.write(f"Error inspecting DDGS.news: {e}\n")
