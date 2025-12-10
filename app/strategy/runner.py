import asyncio
from typing import Dict
from uuid import UUID
import json

from sqlalchemy.orm import Session

from db import SessionLocal
from models import StrategyInstance, StrategyInstanceStatusEnum
from strategy.base import StrategyContext, Strategy
from strategy.registry import get_strategy_class
from services.broker import PaperBroker
from services.market import MarketDataService

class StrategyRunner:
    """
    Ejecuta todas las estrategias en paralelo dentro del proceso FastAPI.
    """

    def __init__(self):
        self._tasks: Dict[UUID, asyncio.Task] = {}
        self._strategies: Dict[UUID, Strategy] = {}
        self._contexts: Dict[UUID, StrategyContext] = {}

        self._market_data = MarketDataService()
        self._broker = PaperBroker(self._market_data)

    def _create_ctx(self, strategy_instance_id: UUID) -> StrategyContext:
        return StrategyContext(
            strategy_instance_id=strategy_instance_id,
            broker=self._broker,
            market_data=self._market_data,
            db_session_factory=SessionLocal,
        )

    async def start_instance(self, instance_id: UUID):
        if instance_id in self._tasks:
            return

        db: Session = SessionLocal()
        try:
            instance = db.query(StrategyInstance).get(instance_id)
            if instance is None:
                raise ValueError("StrategyInstance not found")

            strategy_cls = get_strategy_class(instance.strategy_type)
            params = json.loads(instance.params or "{}")
            strategy = strategy_cls(params=params)
            ctx = self._create_ctx(instance_id)

            self._strategies[instance_id] = strategy
            self._contexts[instance_id] = ctx

            async def strategy_loop():
                try:
                    await strategy.on_start(ctx)
                    while True:
                        await strategy.on_tick(ctx)
                        await asyncio.sleep(5)
                except asyncio.CancelledError:
                    print(f"Strategy {instance_id} cancelled")
                except Exception as e:
                    print(f"Strategy {instance_id} error: {e}")
                    db_err = SessionLocal()
                    try:
                        inst2 = db_err.query(StrategyInstance).get(instance_id)
                        if inst2:
                            inst2.status = StrategyInstanceStatusEnum.ERROR
                            db_err.commit()
                    finally:
                        db_err.close()

            task = asyncio.create_task(strategy_loop(), name=f"strategy-{instance_id}")
            self._tasks[instance_id] = task

            instance.status = StrategyInstanceStatusEnum.RUNNING
            db.commit()
        finally:
            db.close()

    async def stop_instance(self, instance_id: UUID):
        task = self._tasks.pop(instance_id, None)
        self._strategies.pop(instance_id, None)
        self._contexts.pop(instance_id, None)

        if task:
            task.cancel()

        db: Session = SessionLocal()
        try:
            inst = db.query(StrategyInstance).get(instance_id)
            if inst:
                inst.status = StrategyInstanceStatusEnum.STOPPED
                db.commit()
        finally:
            db.close()

    async def handle_news_signal(self, signal):
        """
        Para el futuro: broadcast de noticias a todas las estrategias.
        """
        for instance_id, strategy in self._strategies.items():
            ctx = self._contexts[instance_id]
            await strategy.on_news(ctx, signal)
