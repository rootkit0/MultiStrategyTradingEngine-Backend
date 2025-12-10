import requests
from datetime import datetime

from db import SessionLocal
import models

BINANCE_URL = "https://api.binance.com/api/v3/klines"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "PAXGUSDT",
]

# Intervalo de las velas
INTERVAL = "1m"


def fetch_klines(symbol, start_ms, end_ms):
    """
    Descarga velas de Binance entre start_ms y end_ms (milisegundos)
    para un símbolo y un intervalo dados.
    """
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    }
    resp = requests.get(BINANCE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def load_market_data():
    db = SessionLocal()
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    one_month_ms = 30 * 24 * 60 * 60 * 1000

    for symbol in SYMBOLS:
        print("=== {} ===".format(symbol))

        # Buscar la última vela que tenemos en BD para este símbolo+intervalo
        last = (
            db.query(models.Candle)
            .filter(
                models.Candle.symbol == symbol,
                models.Candle.interval == INTERVAL,
            )
            .order_by(models.Candle.open_time.desc())
            .first()
        )

        if last is None:
            # Primera vez que cargamos este símbolo
            start_ms = now_ms - one_month_ms
            print("No hay datos en BD. Descargando 1 mes desde {}.".format(start_ms))
        else:
            # Continuar a partir del siguiente minuto
            start_ms = int(last.open_time) + 60_000
            print(
                "Última vela en BD: {}. Empezando en {}.".format(
                    last.open_time, start_ms
                )
            )

        if start_ms >= now_ms:
            print("No hay nada nuevo que descargar para {}.".format(symbol))
            continue

        ts = start_ms
        while ts < now_ms:
            batch_end = min(ts + 1000 * 60_000, now_ms)
            print(
                "Descargando velas {} de {} a {}...".format(
                    symbol, ts, batch_end
                )
            )

            try:
                klines = fetch_klines(symbol, ts, batch_end)
            except Exception as e:
                print("Error descargando velas para {}: {}".format(symbol, e))
                break

            if not klines:
                print("Sin velas devueltas para {}. Saliendo del bucle.".format(symbol))
                break

            # Insertar velas en la BD
            for k in klines:
                candle = models.Candle(
                    symbol=symbol,
                    interval=INTERVAL,
                    open_time=k[0],
                    open=k[1],
                    high=k[2],
                    low=k[3],
                    close=k[4],
                    volume=k[5],
                    close_time=k[6],
                )
                db.add(candle)

            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print("Error haciendo commit para {}: {}".format(symbol, e))
                break

            print("Guardadas {} velas para {}.".format(len(klines), symbol))

            ts = klines[-1][0] + 60_000

            if len(klines) < 1000:
                break

    db.close()

if __name__ == "__main__":
    load_market_data()
