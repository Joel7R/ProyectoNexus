import asyncio
import os
import sys

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.news_scout import NewsScoutAgent
from agents.event_scout import EventScoutAgent
from agents.time_estimator import TimeEstimatorAgent
from agents.chronos import ChronosAgent
from agents.deal_scout import DealScoutAgent
from llm_config import LLMManager

async def test_all():
    print("=== STARTING AGENT SYSTEM CHECK ===")
    
    # Check 1: NewsScout
    print("\n[1/5] Testing NewsScout...")
    try:
        news_agent = NewsScoutAgent()
        # Updated signature: game, query
        result = await news_agent.search("Elden Ring", "latest news")
        # Result is NewsResult (pydantic), access via attributes or .dict()
        if result:
            print("[PASS] NewsScout OK")
            print(f"   Summary: {result.summary[:50]}...")
        else:
            print(f"[FAIL] NewsScout FAILED")
    except Exception as e:
        print(f"[FAIL] NewsScout EXCEPTION: {e}")

    # Check 2: EventScout
    print("\n[2/5] Testing EventScout...")
    try:
        event_agent = EventScoutAgent()
        result = await event_agent.get_live_events()
        if result.get('success'):
            print("[PASS] EventScout OK")
            print(f"   Live Events: {result.get('count', 0)}")
        else:
            print(f"[FAIL] EventScout FAILED")
    except Exception as e:
        print(f"[FAIL] EventScout EXCEPTION: {e}")

    # Check 3: TimeEstimator
    print("\n[3/5] Testing TimeEstimator...")
    try:
        time_agent = TimeEstimatorAgent()
        result = await time_agent.estimate_game_time("Hollow Knight")
        if result.get('success'):
            print("[PASS] TimeEstimator OK")
            # Result structure from updated agent
            print(f"   Main Story: {result['artifact']['data']['main_story']}h")
        else:
            print(f"[FAIL] TimeEstimator FAILED: {result.get('summary')}")
    except Exception as e:
        print(f"[FAIL] TimeEstimator EXCEPTION: {e}")

    # Check 4: Chronos
    print("\n[4/5] Testing Chronos...")
    try:
        chronos_agent = ChronosAgent()
        # Fixed method name: get_lore
        result = await chronos_agent.get_lore("Celeste", "Madeline", "low")
        if result.get('success'):
            print("[PASS] Chronos OK")
            print(f"   Summary: {result['summary'][:50]}...")
        else:
            print(f"[FAIL] Chronos FAILED")
    except Exception as e:
        print(f"[FAIL] Chronos EXCEPTION: {e}")

    # Check 5: DealScout
    print("\n[5/5] Testing DealScout...")
    try:
        deal_agent = DealScoutAgent()
        result = await deal_agent.search_deals("Stardew Valley")
        if result.get('success'):
            print("[PASS] DealScout OK")
            print(f"   Deals found: {len(result['deals'])}")
        else:
            print(f"[FAIL] DealScout FAILED: {result.get('summary')}")
    except Exception as e:
        print(f"[FAIL] DealScout EXCEPTION: {e}")

    print("\n=== SYSTEM CHECK COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_all())
