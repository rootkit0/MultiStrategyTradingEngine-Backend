from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import json

import models, schemas
from api.deps import get_db
from strategy.runner import StrategyRunner
from typing import Optional, List

router = APIRouter(prefix="/api/strategy-instances", tags=["strategy-instances"])

runner: Optional[StrategyRunner] = None

def set_runner(r: StrategyRunner):
    global runner
    runner = r

@router.post("", response_model=schemas.StrategyInstanceRead)
def create_strategy_instance(
    data: schemas.StrategyInstanceCreate,
    db: Session = Depends(get_db),
):
    instance = models.StrategyInstance(
        name=data.name,
        strategy_type=data.strategy_type,
        params=json.dumps(data.params),
        initial_equity=data.initial_equity,
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

@router.get("", response_model=List[schemas.StrategyInstanceListItem])
def list_strategy_instances(db: Session = Depends(get_db)):
    return db.query(models.StrategyInstance).all()

@router.get("/{instance_id}", response_model=schemas.StrategyInstanceRead)
def get_strategy_instance(instance_id: UUID, db: Session = Depends(get_db)):
    instance = db.query(models.StrategyInstance).get(instance_id)
    if not instance:
        raise HTTPException(404, "Not found")
    return instance

@router.post("/{instance_id}/start")
async def start_strategy_instance(instance_id: UUID, db: Session = Depends(get_db)):
    if runner is None:
        raise HTTPException(500, "Runner not initialized")

    instance = db.query(models.StrategyInstance).get(instance_id)
    if not instance:
        raise HTTPException(404, "Not found")

    await runner.start_instance(instance_id)
    return {"status": "started"}

@router.post("/{instance_id}/stop")
async def stop_strategy_instance(instance_id: UUID, db: Session = Depends(get_db)):
    if runner is None:
        raise HTTPException(500, "Runner not initialized")

    instance = db.query(models.StrategyInstance).get(instance_id)
    if not instance:
        raise HTTPException(404, "Not found")

    await runner.stop_instance(instance_id)
    return {"status": "stopped"}
