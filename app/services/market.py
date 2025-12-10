import random

class MarketDataService:
    """
    Servicio de datos de mercado simulado.
    Mantiene precios en memoria y hace un random walk.
    """

    def __init__(self):
        self._prices = {
            "BTCUSDT": 30000.0,
        }

    async def get_last_price(self, symbol: str) -> float:
        price = self._prices.get(symbol, 30000.0)
        change = random.uniform(-0.005, 0.005)
        new_price = price * (1 + change)
        self._prices[symbol] = new_price
        return new_price
