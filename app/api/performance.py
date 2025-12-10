from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

import models, schemas
from api.deps import get_db
from services.pnl import compute_performance_for_instance

router = APIRouter(prefix="/instances", tags=["performance"])

@router.get("/{instance_id}/performance", response_model=schemas.PerformanceRead)
def get_performance(instance_id: UUID, db: Session = Depends(get_db)):
    instance = db.query(models.StrategyInstance).get(instance_id)
    if not instance:
        raise HTTPException(404, "Not found")

    perf = compute_performance_for_instance(db, instance)
    now = datetime.utcnow()

    return schemas.PerformanceRead(
        strategy_instance_id=instance.id,
        initial_equity=instance.initial_equity,
        equity=perf["equity"],
        realized_pnl=perf["realized_pnl"],
        unrealized_pnl=perf["unrealized_pnl"],
        pnl_total_pct=perf["pnl_total_pct"],
        timestamp=now,
    )
