import requests
from datetime import datetime, timedelta
from db import SessionLocal
from models import Candle

BASE_URL = "https://api.binance.com/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XAUUSDT"]
INTERVAL = "1m"


def fetch_candles(symbol: str, start: int, end: int):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "startTime": start,
        "endTime": end,
        "limit": 1000,
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    return r.json()


def load_market_data():
    db = SessionLocal()
    now_ms = int(datetime.utcnow().timestamp() * 1000)

    one_month_ms = 30 * 24 * 60 * 60 * 1000

    for symbol in SYMBOLS:
        last = (
            db.query(models.Candle)
            .filter(models.Candle.symbol == symbol)
            .order_by(models.Candle.open_time.desc())
            .first()
        )

        # FIRST TIME → DOWNLOAD 1 FULL MONTH
        if last is None:
            print(f"[{symbol}] No data found, downloading 1 month...")
            start_ts = now_ms - one_month_ms
        else:
            start_ts = last.open_time + 60_000  # next minute

        end_ts = now_ms

        print(f"[{symbol}] Fetching candles from {start_ts} to {end_ts}")

        ts = start_ts
        while ts < end_ts:
            batch_end = min(ts + (1000 * 60_000), end_ts)
            candles = fetch_candles(symbol, ts, batch_end)

            for c in candles:
                db.add(models.Candle(
                    symbol=symbol,
                    interval=INTERVAL,
                    open_time=c[0],
                    open=c[1],
                    high=c[2],
                    low=c[3],
                    close=c[4],
                    volume=c[5],
                    close_time=c[6],
                ))

            db.commit()
            print(f"[{symbol}] Stored {len(candles)} candles")

            if len(candles) < 1000:
                break

            ts = candles[-1][0] + 60_000

    db.close()


if __name__ == "__main__":
    load_market_data()

