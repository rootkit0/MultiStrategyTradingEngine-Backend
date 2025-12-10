from fastapi import FastAPI

from db import engine, Base, SessionLocal
from models import StrategyInstance, StrategyInstanceStatusEnum
from strategy.runner import StrategyRunner

# import the objects directly from api.py
from api import strategy_instances, strategy_types, performance, trades

app = FastAPI(title="Trading Backend Demo")

Base.metadata.create_all(bind=engine)

runner = StrategyRunner()
strategy_instances.set_runner(runner)

app.include_router(strategy_types.router)
app.include_router(strategy_instances.router)
app.include_router(performance.router)
app.include_router(trades.router)

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

