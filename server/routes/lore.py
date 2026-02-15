from fastapi import APIRouter
from server.services.lore_generator import LoreGenerator

router = APIRouter()
service = LoreGenerator()

@router.get("/")
async def health():
    return {"status": "Lore Router Ready"}
