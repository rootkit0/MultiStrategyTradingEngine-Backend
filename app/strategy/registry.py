from typing import Dict, Type, List
from typing_extensions import TypedDict
from strategy.base import Strategy
from strategies.btc_trend import BTCTrendStrategy

class StrategyMeta(TypedDict):
    key: str
    display_name: str
    description: str
    class_ref: Type[Strategy]

STRATEGY_REGISTRY: Dict[str, StrategyMeta] = {
    "btc_trend": {
        "key": "btc_trend",
        "display_name": "BTC Trend Following (Demo)",
        "description": "Estrategia de ejemplo que compra/vende BTC cuando el precio se mueve un 0.1%.",
        "class_ref": BTCTrendStrategy,
    },
}

def get_strategy_class(strategy_type: str) -> Type[Strategy]:
    if strategy_type not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    return STRATEGY_REGISTRY[strategy_type]["class_ref"]

def list_strategy_types() -> List[StrategyMeta]:
    return list(STRATEGY_REGISTRY.values())
