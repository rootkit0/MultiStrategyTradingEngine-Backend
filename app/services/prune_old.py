from datetime import datetime, timedelta
from db import SessionLocal
import models

def prune_old():
    db = SessionLocal()

    cutoff_ts = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)

    deleted = (
        db.query(models.Candle)
        .filter(models.Candle.open_time < cutoff_ts)
        .delete()
    )

    db.commit()
    db.close()

    print(f"Deleted {deleted} old candles")


if __name__ == "__main__":
    prune_old()
