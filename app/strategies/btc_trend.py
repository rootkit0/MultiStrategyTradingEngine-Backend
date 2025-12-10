from . import *
from strategy.base import Strategy, StrategyContext

class BTCTrendStrategy(Strategy):
    """
    Estrategia de ejemplo simple.
    - Pide precio simulado de BTCUSDT.
    - Si sube más de 0.1% desde el tick anterior -> hace un 'buy' pequeño.
    - Si baja más de 0.1% -> hace un 'sell' pequeño.
    Es solo para ver trades y PnL moverse.
    """

    def __init__(self, params):
        super().__init__(params)
        self.last_price: float | None = None

    async def on_start(self, ctx: StrategyContext):
        symbol = self.params.get("symbol", "BTCUSDT")
        price = await ctx.get_price(symbol)
        self.last_price = price
        ctx.log(f"BTCTrendStrategy started at price {price:.2f}")

    async def on_tick(self, ctx: StrategyContext):
        symbol = self.params.get("symbol", "BTCUSDT")
        qty = float(self.params.get("qty", 0.001))

        price = await ctx.get_price(symbol)
        if self.last_price is None:
            self.last_price = price
            return

        change = (price - self.last_price) / self.last_price

        if change > 0.001:
            ctx.log(f"Price up {change*100:.2f}%, BUY {qty}")
            await ctx.buy(symbol, qty)
        elif change < -0.001:
            ctx.log(f"Price down {change*100:.2f}%, SELL {qty}")
            await ctx.sell(symbol, qty)

        self.last_price = price
