from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models import db_models
from app.models.schemas import CategoryBreakdown, PredictionResult
from app.services.ml_predictor import predict_future_footprint
from app.routers.auth import oauth2_scheme

router = APIRouter()

@router.post("/forecast", response_model=PredictionResult, status_code=200)
def forecast(breakdown: CategoryBreakdown, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    from app.core.security import decode_access_token
    historical_totals = None
    if token:
        email = decode_access_token(token)
        if email:
            user = db.query(db_models.User).filter(db_models.User.email == email).first()
            if user:
                records = db.query(db_models.CarbonRecord.total_kg).filter(db_models.CarbonRecord.user_id == user.id).order_by(db_models.CarbonRecord.calculated_at.asc()).all()
                if len(records) >= 3:
                    historical_totals = [r.total_kg for r in records]
    return predict_future_footprint(breakdown, historical_totals=historical_totals)
