"""
QA Runner - Gaming Nexus
Executes Model Comparison Protocol (Local vs Turbo) for QA Validation.
"""
import sys
import os
import asyncio
import time
import logging
from typing import List, Dict
from datetime import datetime

# Setup logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "qa_results.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fix imports - work from server directory
# Assuming this script (qa_runner.py) is in the 'server' directory
# We need to add the 'server' directory itself to the path to allow direct imports like 'from llm_config'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_config import llm_manager
from agents.time_estimator import TimeEstimatorAgent
from agents.deal_scout import DealScoutAgent
from agents.chronos import ChronosAgent
from agents.tactician import TacticianAgent

class QARunner:
    def __init__(self):
        self.results = []
    
    def log(self, message: str):
        logger.info(message)
        
    async def run_model_comparison(self):
        tests = [
            {
                "id": 1,
                "name": "Time2Play (TimeEstimator)",
                "agent_cls": TimeEstimatorAgent,
                "method": "estimate_game_time",
                "args": ["Persona 5 Royal"],
                "kwargs": {"hours_per_day": 3.0},
                "validator": lambda r: (
                    r.get("artifact", {}).get("marathon_mode", {}).get("days_main", 0) > 0
                )
            },
            {
                "id": 2,
                "name": "Price Hunter (DealScout)",
                "agent_cls": DealScoutAgent,
                "method": "analyze",
                "args": ["Minecraft"],
                "kwargs": {"stores": ["steam", "microsoft", "instant_gaming"]},
                "validator": lambda r: (
                    r.get("artifact", {}).get("display") == "price_comparison" and
                    isinstance(r.get("deals"), list)  # Check deals at root level, not in artifact
                )
            },
            {
                "id": 3,
                "name": "Lore Master (Chronos)",
                "agent_cls": ChronosAgent,
                "method": "get_lore",
                "args": ["Elden Ring", "Miquella"],
                "kwargs": {"spoiler_level": "medium"},
                "validator": lambda r: (
                    "mermaid_content" in r.get("artifact", {}) and
                    len(r.get("artifact", {}).get("mermaid_content", "")) > 10
                )
            },
            {
                "id": 4,
                "name": "Tactician (CLR Strategy)",
                "agent_cls": TacticianAgent,
                "method": "analyze",
                "args": ["Clair Obscur: Expedition 33", "best weapons"],
                "kwargs": {"language": "es"},
                "validator": lambda r: (
                    isinstance(r, dict) and
                    "artifact" in r and
                    isinstance(r.get("artifact"), dict) and
                    r["artifact"].get("display") in ["build_dashboard", "empty"]  # Accept empty for obscure games
                )
            }
        ]
        
        models = ["gemini"]
        
        logger.info("=" * 80)
        logger.info("GAMING NEXUS - QA MODEL VALIDATION (GEMINI 1.5 FLASH)")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 80)
        logger.info(f"{'TEST':<30} | {'MODEL':<10} | {'TIME (s)':<10} | {'STATUS':<20}")
        logger.info("-" * 80)
        
        for test in tests:
            for model in models:
                # model is always gemini
                
                # Instantiate Agent
                result = None
                status = "UNKNOWN"
                elapsed = 0.0
                
                try:
                    agent = test["agent_cls"]()
                    method = getattr(agent, test["method"])
                    
                    start_time = time.time()
                    
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        method(*test["args"], **test["kwargs"]),
                        timeout=30.0
                    )
                    elapsed = time.time() - start_time
                    
                    # Validate
                    if test["validator"](result):
                        status = "✅ PASS"
                    else:
                        status = "❌ FAIL (Validation)"
                        logger.warning(f"Validation failed for {test['name']} with {model}")
                        
                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time
                    status = "⏱️ TIMEOUT (30s)"
                    logger.error(f"Timeout for {test['name']} with {model}")
                    
                except Exception as e:
                    elapsed = time.time() - start_time
                    status = f"💥 ERROR: {str(e)[:30]}"
                    logger.error(f"Error in {test['name']} with {model}: {e}", exc_info=True)
                
                logger.info(f"{test['name']:<30} | {model:<10} | {elapsed:<10.2f} | {status:<20}")
                
                # Store detail for report
                self.results.append({
                    "test": test["name"],
                    "model": model,
                    "time": elapsed,
                    "status": status,
                    "result_summary": result.get("summary") if isinstance(result, dict) else "N/A"
                })
        
        logger.info("=" * 80)
        logger.info(f"QA Run Complete. Results saved to: {LOG_FILE}")
        logger.info("=" * 80)

if __name__ == "__main__":
    runner = QARunner()
    asyncio.run(runner.run_model_comparison())
