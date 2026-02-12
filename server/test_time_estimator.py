import asyncio
import os
import sys

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.time_estimator import TimeEstimatorAgent

async def test_time_estimator():
    print("Testing TimeEstimatorAgent...")
    agent = TimeEstimatorAgent()
    
    try:
        print("\nTest: Hollow Knight")
        result = await agent.estimate_game_time("Hollow Knight")
        if result['success']:
            print(f"[PASS] Main Story: {result['times']['main']}h")
        else:
            print(f"[FAIL] {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_time_estimator())
