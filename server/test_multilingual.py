import asyncio
import os
from agents.news_scout import NewsScoutAgent
from agents.tactician import TacticianAgent
from agents.guide_navigator import GuideNavigatorAgent

# Set dummy env vars if needed, or rely on system env
os.environ["OLLAMA_MODEL"] = "llama3.2"

async def test_news_scout():
    print("\n--- Testing NewsScout (ES) ---")
    agent = NewsScoutAgent()
    # Test Spanish search
    result = await agent.search(game="League of Legends", query="nuevos parches y notas", language="es")
    print(f"Summary: {result.summary[:100]}...")
    if result.artifact and "rows" in result.artifact:
        print(f"Artifact Items ({len(result.artifact['rows'])}):")
        for item in result.artifact['rows'][:2]:
            print(f" - [{item.get('source_lang')}] {item.get('title')}")
            if item.get('source_lang') not in ['es', 'en']:
                print("   [WARNING] source_lang missing or invalid")
    else:
        print("[WARNING] No artifact items found")

async def test_tactician():
    print("\n--- Testing Tactician (ES) ---")
    agent = TacticianAgent()
    result = await agent.analyze(game="Elden Ring", query="Rivers of Blood build", language="es")
    print(f"Summary: {result.summary[:100]}...")
    # Check if summary seems to be in Spanish
    if "construcción" in result.summary.lower() or "build" in result.summary.lower() or "sangrado" in result.summary.lower():
         print("Validation: Output seems relevant.")
    else:
         print("Validation: Check output language manually.")

async def test_guide_navigator():
    print("\n--- Testing GuideNavigator (ES) ---")
    agent = GuideNavigatorAgent()
    result = await agent.find_solution(game="Zelda Breath of the Wild", query="como conseguir la espada maestra", language="es")
    print(f"Summary: {result.summary[:100]}...")
    if result.steps:
        print(f"Steps found: {len(result.steps)}")
        print(f"Step 1 Title: {result.steps[0].get('title')}")
    else:
        print("[WARNING] No steps found")

async def main():
    await test_news_scout()
    await test_tactician()
    await test_guide_navigator()

if __name__ == "__main__":
    asyncio.run(main())
