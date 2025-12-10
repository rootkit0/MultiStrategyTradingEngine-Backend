from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

import models, schemas
from api.deps import get_db
from typing import List

router = APIRouter(prefix="/api/strategy-instances", tags=["trades-positions"])

@router.get("/{instance_id}/trades", response_model=List[schemas.TradeRead])
def get_trades(instance_id: UUID, db: Session = Depends(get_db)):
    inst = db.query(models.StrategyInstance).get(instance_id)
    if not inst:
        raise HTTPException(404, "Not found")

    return (
        db.query(models.Trade)
        .filter(models.Trade.strategy_instance_id == instance_id)
        .order_by(models.Trade.created_at.desc())
        .all()
    )

@router.get("/{instance_id}/positions", response_model=List[schemas.PositionRead])
def get_positions(instance_id: UUID, db: Session = Depends(get_db)):
    inst = db.query(models.StrategyInstance).get(instance_id)
    if not inst:
        raise HTTPException(404, "Not found")

    return (
        db.query(models.Position)
        .filter(models.Position.strategy_instance_id == instance_id)
        .all()
    )
