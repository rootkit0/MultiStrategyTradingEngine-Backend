from sqlalchemy.orm import Session
import models

def compute_performance_for_instance(db: Session, instance: models.StrategyInstance):
    trades = (
        db.query(models.Trade)
        .filter(models.Trade.strategy_instance_id == instance.id)
        .all()
    )
    realized = sum(t.realized_pnl for t in trades)

    unrealized = 0.0

    equity = instance.initial_equity + realized + unrealized
    pnl_total_pct = (
        (equity - instance.initial_equity) / instance.initial_equity * 100
        if instance.initial_equity
        else 0.0
    )

    return {
        "equity": equity,
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "pnl_total_pct": pnl_total_pct,
    }
