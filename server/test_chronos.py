import asyncio
import os
import sys

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chronos import ChronosAgent

async def test_chronos():
    print("Testing ChronosAgent...")
    agent = ChronosAgent()
    
    # Test 1: Simple query (no spoiler)
    try:
        print("\nTest 1: Celeste (no spoiler)")
        result = await agent.get_story("Celeste", "none")
        if result['success']:
            print(f"[PASS] Found story: {len(result['summary'])} chars")
        else:
            print(f"[FAIL] {result.get('message')}")
            print(f"Reasoning: {result.get('reasoning')}")
    except Exception as e:
        print(f"[ERROR] Test 1: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chronos())
