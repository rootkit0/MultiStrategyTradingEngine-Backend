from fastapi import APIRouter
from strategy.registry import list_strategy_types
from schemas import StrategyTypeRead
from typing import List

router = APIRouter(prefix="/api/strategies", tags=["strategies"])

@router.get("", response_model=List[StrategyTypeRead])
def get_strategy_types():
    metas = list_strategy_types()
    return [
        StrategyTypeRead(
            key=m["key"],
            display_name=m["display_name"],
            description=m["description"],
        )
        for m in metas
    ]
