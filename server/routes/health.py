from fastapi import APIRouter
from server.services.llm_service import llm_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    llm_health = llm_service.check_health()
    return {
        "status": "healthy",
        "llm_service": llm_health,
        "version": "1.0.0"
    }
