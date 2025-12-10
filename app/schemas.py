from typing import Any, Dict, Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, validator
from models import StrategyInstanceStatusEnum
import json

class StrategyTypeRead(BaseModel):
    key: str
    display_name: str
    description: str

class StrategyInstanceCreate(BaseModel):
    name: str
    strategy_type: str
    params: Dict[str, Any]
    initial_equity: float

class StrategyInstanceListItem(BaseModel):
    id: UUID
    name: str
    strategy_type: str
    status: StrategyInstanceStatusEnum
    created_at: datetime

    class Config:
        orm_mode = True

class TradeRead(BaseModel):
    id: UUID
    symbol: str
    side: str
    qty: float
    price: float
    fee: float
    realized_pnl: float
    created_at: datetime

    class Config:
        orm_mode = True

class PositionRead(BaseModel):
    id: UUID
    symbol: str
    side: str
    qty: float
    avg_price: float
    updated_at: datetime

    class Config:
        orm_mode = True

class PerformanceRead(BaseModel):
    strategy_instance_id: UUID
    initial_equity: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    pnl_total_pct: float
    timestamp: datetime

class StrategyInstanceRead(BaseModel):
    id: UUID
    name: str
    strategy_type: str
    params: Dict[str, Any]
    initial_equity: float
    status: StrategyInstanceStatusEnum
    created_at: datetime
    updated_at: Optional[datetime]

    @validator("params")
    @classmethod
    def parse_params(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return {}
