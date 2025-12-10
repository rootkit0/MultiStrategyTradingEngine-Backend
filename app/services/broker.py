from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session

from db import SessionLocal
import models
from services.market import MarketDataService

class Broker(ABC):
    @abstractmethod
    async def place_order(self, strategy_instance_id: UUID, symbol: str, side: str, qty: float):
        ...

class PaperBroker(Broker):
    """
    Ejecuta órdenes contra el precio simulado.
    Calcula posiciones y PnL realizado.
    """

    def __init__(self, market_data: MarketDataService):
        self._market_data = market_data

    async def place_order(self, strategy_instance_id: UUID, symbol: str, side: str, qty: float):
        price = await self._market_data.get_last_price(symbol)
        fee = 0.0

        db: Session = SessionLocal()
        try:
            pos = (
                db.query(models.Position)
                .filter(
                    models.Position.strategy_instance_id == strategy_instance_id,
                    models.Position.symbol == symbol,
                )
                .one_or_none()
            )

            realized_pnl = 0.0
            order_side = side.lower()

            if pos is None:
                # Abrimos nueva posición
                pos_side = "long" if order_side == "buy" else "short"
                pos = models.Position(
                    strategy_instance_id=strategy_instance_id,
                    symbol=symbol,
                    side=pos_side,
                    qty=qty,
                    avg_price=price,
                )
                db.add(pos)
            else:
                # Ya hay posición
                if pos.side == "long":
                    if order_side == "buy":
                        # aumentar long
                        new_qty = pos.qty + qty
                        pos.avg_price = (pos.avg_price * pos.qty + price * qty) / new_qty
                        pos.qty = new_qty
                    else:  # sell contra long -> cerrar parcial o total
                        if qty < pos.qty:
                            # cierre parcial
                            realized_pnl += (price - pos.avg_price) * qty
                            pos.qty -= qty
                        elif qty == pos.qty:
                            realized_pnl += (price - pos.avg_price) * qty
                            db.delete(pos)
                        else:
                            # flip: cerramos todo long y abrimos short con el resto
                            close_qty = pos.qty
                            realized_pnl += (price - pos.avg_price) * close_qty
                            remaining = qty - close_qty
                            pos.side = "short"
                            pos.qty = remaining
                            pos.avg_price = price
                else:  # pos.side == "short"
                    if order_side == "sell":
                        # aumentar short
                        new_qty = pos.qty + qty
                        pos.avg_price = (pos.avg_price * pos.qty + price * qty) / new_qty
                        pos.qty = new_qty
                    else:  # buy contra short -> cerrar parcial o total
                        if qty < pos.qty:
                            realized_pnl += (pos.avg_price - price) * qty
                            pos.qty -= qty
                        elif qty == pos.qty:
                            realized_pnl += (pos.avg_price - price) * qty
                            db.delete(pos)
                        else:
                            close_qty = pos.qty
                            realized_pnl += (pos.avg_price - price) * close_qty
                            remaining = qty - close_qty
                            pos.side = "long"
                            pos.qty = remaining
                            pos.avg_price = price

            trade = models.Trade(
                strategy_instance_id=strategy_instance_id,
                symbol=symbol,
                side=order_side,
                qty=qty,
                price=price,
                fee=fee,
                realized_pnl=realized_pnl,
            )
            db.add(trade)

            db.commit()
        finally:
            db.close()
