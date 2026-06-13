from fastapi import APIRouter, status
from app.models.schemas import CategoryBreakdown, Tip
from app.services.ml_predictor import generate_tips
from typing import List

router = APIRouter()

@router.post("/personalized", response_model=List[Tip], status_code=200)
def get_tips(breakdown: CategoryBreakdown) -> List[Tip]:
    return generate_tips(breakdown)
