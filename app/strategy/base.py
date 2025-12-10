from abc import ABC, abstractmethod
from typing import Any, Dict, Callable

from services.market import MarketDataService
from services.broker import Broker

class StrategyContext:
    def __init__(
        self,
        strategy_instance_id,
        broker: Broker,
        market_data: MarketDataService,
        db_session_factory: Callable,
    ):
        self.strategy_instance_id = strategy_instance_id
        self._broker = broker
        self._market_data = market_data
        self._db_session_factory = db_session_factory

    async def buy(self, symbol: str, qty: float):
        await self._broker.place_order(
            strategy_instance_id=self.strategy_instance_id,
            symbol=symbol,
            side="buy",
            qty=qty,
        )

    async def sell(self, symbol: str, qty: float):
        await self._broker.place_order(
            strategy_instance_id=self.strategy_instance_id,
            symbol=symbol,
            side="sell",
            qty=qty,
        )

    async def get_price(self, symbol: str) -> float:
        return await self._market_data.get_last_price(symbol)

    def log(self, msg: str):
        print(f"[{self.strategy_instance_id}] {msg}")


class Strategy(ABC):
    """
    Base para todas las estrategias.
    """
    def __init__(self, params: Dict[str, Any]):
        self.params = params

    @abstractmethod
    async def on_start(self, ctx: StrategyContext):
        """
        Se llama una vez al arrancar la instancia de estrategia.
        """
        ...

    @abstractmethod
    async def on_tick(self, ctx: StrategyContext):
        """
        Se llama cada N segundos (definido en el runner).
        Aquí puedes mirar precios, calcular señales y enviar órdenes.
        """
        ...

    async def on_news(self, ctx: StrategyContext, news_signal: Dict[str, Any]):
        """
        Opcional: reaccionar a señales de noticias.
        """
        return
