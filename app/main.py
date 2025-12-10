from fastapi import FastAPI

from db import engine, Base, SessionLocal
from models import StrategyInstance, StrategyInstanceStatusEnum
from strategy.runner import StrategyRunner

from api.strategy_instances import router as strategy_instances_router, set_runner
from api.strategy_types import router as strategy_types_router
from api.performance import router as performance_router
from api.trades import router as trades_router

app = FastAPI(title="Trading Backend Demo")

Base.metadata.create_all(bind=engine)

runner = StrategyRunner()
set_runner(runner)

app.include_router(strategy_instances_router)
app.include_router(strategy_types_router)
app.include_router(performance_router)
app.include_router(trades_router)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        autostart_instances = (
            db.query(StrategyInstance)
            .filter(StrategyInstance.status == StrategyInstanceStatusEnum.RUNNING)
            .all()
        )
        for inst in autostart_instances:
            await runner.start_instance(inst.id)
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

