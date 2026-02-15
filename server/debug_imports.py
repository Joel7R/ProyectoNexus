import sys
import warnings

# Filter warnings to ensure we see them
warnings.simplefilter("always")

print("--- Starting Import Debug ---")

try:
    print("Importing fastapi...")
    from fastapi import FastAPI
    print("OK fastapi")
except Exception as e:
    print(f"Error fastapi: {e}")

try:
    print("Importing pydantic...")
    from pydantic import BaseModel, Field
    print("OK pydantic")
except Exception as e:
    print(f"Error pydantic: {e}")

try:
    print("Importing sse_starlette...")
    from sse_starlette.sse import EventSourceResponse
    print("OK sse_starlette")
except Exception as e:
    print(f"Error sse_starlette: {e}")

try:
    print("Importing agents...")
    from agents.news_scout import NewsScoutAgent
    print("OK agents.news_scout")
    from agents.deal_scout import DealScoutAgent
    print("OK agents.deal_scout")
    from agents.event_scout import EventScoutAgent
    print("OK agents.event_scout")
except Exception as e:
    print(f"Error agents: {e}")

try:
    print("Importing langchain...")
    import langchain
    print(f"OK langchain {langchain.__version__}")
except Exception as e:
    print(f"Error langchain: {e}")

try:
    print("Importing google.generativeai...")
    import google.generativeai
    print("OK google.generativeai")
except Exception as e:
    print(f"Error google: {e}")
