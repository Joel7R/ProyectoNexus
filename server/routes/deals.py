from fastapi import APIRouter
from server.services.price_tracker_service import PriceTrackerService

router = APIRouter()
service = PriceTrackerService()

@router.get("/")
async def health():
    return {"status": "Deals Router Ready"}
