"""
KuCoin public REST API client for OHLCV (candlestick) data.
No API credentials required for market data endpoints.
"""
import time
import requests
import pandas as pd

import config

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "crypto-signals-bot/1.0"})


def _unix_now() -> int:
    return int(time.time())


def fetch_candles(symbol: str, limit: int = config.CANDLE_LIMIT) -> pd.DataFrame:
    """
    Fetch the most recent `limit` closed OHLCV candles for `symbol`
    at the configured interval.

    KuCoin candle endpoint returns rows newest-first as:
      [time, open, close, high, low, volume, turnover]
    """
    end_ts = _unix_now()
    # Each 1hour candle is 3600 seconds
    interval_seconds = _interval_to_seconds(config.INTERVAL)
    start_ts = end_ts - interval_seconds * limit

    url = f"{config.KUCOIN_API_BASE}/api/v1/market/candles"
    params = {
        "symbol": symbol,
        "type": config.INTERVAL,
        "startAt": start_ts,
        "endAt": end_ts,
    }

    resp = _SESSION.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != "200000":
        raise RuntimeError(f"KuCoin API error for {symbol}: {data}")

    candles = data.get("data", [])
    if not candles:
        raise ValueError(f"No candle data returned for {symbol}")

    df = pd.DataFrame(
        candles,
        columns=["time", "open", "close", "high", "low", "volume", "turnover"],
    )
    df = df.astype(
        {
            "time": "int64",
            "open": "float64",
            "close": "float64",
            "high": "float64",
            "low": "float64",
            "volume": "float64",
            "turnover": "float64",
        }
    )
    # KuCoin returns newest first — reverse so oldest is row 0
    df = df.sort_values("time").reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df


def _interval_to_seconds(interval: str) -> int:
    mapping = {
        "1min": 60,
        "3min": 180,
        "5min": 300,
        "15min": 900,
        "30min": 1800,
        "1hour": 3600,
        "2hour": 7200,
        "4hour": 14400,
        "6hour": 21600,
        "8hour": 28800,
        "12hour": 43200,
        "1day": 86400,
        "1week": 604800,
    }
    return mapping.get(interval, 3600)
