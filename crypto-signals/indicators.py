"""
Technical indicator calculations and multi-indicator signal scoring.

Indicators used
---------------
- RSI-14          (momentum)
- EMA 9/21/50     (trend)
- MACD            (trend + momentum confirmation)
- Bollinger Bands (volatility / overbought-oversold)
- Stochastic RSI  (sensitive momentum)
- Volume          (breakout confirmation)
- ATR-14          (volatility → price level sizing)

Scoring
-------
Each indicator votes independently. The final score (0–10) reflects how many
agree with the signal direction. Confidence labels:

  0–3  → Low        (signal suppressed by default)
  4–5  → Medium
  6–7  → High
  8–10 → Very High
"""
import pandas as pd
import numpy as np


# ── helpers ──────────────────────────────────────────────────────────────────

def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _fmt(price: float) -> str:
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:,.4f}"
    else:
        return f"{price:,.6f}"


# ── individual indicators ─────────────────────────────────────────────────────

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """RSI using Wilder's smoothing."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_macd(series: pd.Series,
                   fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD line, signal line, and histogram."""
    macd_line = _ema(series, fast) - _ema(series, slow)
    signal_line = _ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger(series: pd.Series, period: int = 20, std: float = 2.0):
    """Bollinger Bands: middle, upper, lower."""
    middle = series.rolling(period).mean()
    stddev = series.rolling(period).std()
    upper = middle + std * stddev
    lower = middle - std * stddev
    return upper, middle, lower


def calculate_stoch_rsi(series: pd.Series,
                         rsi_period: int = 14, stoch_period: int = 14,
                         k_period: int = 3, d_period: int = 3):
    """Stochastic RSI — %K and %D."""
    rsi = calculate_rsi(series, rsi_period)
    rsi_min = rsi.rolling(stoch_period).min()
    rsi_max = rsi.rolling(stoch_period).max()
    stoch = (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan) * 100
    k = stoch.rolling(k_period).mean()
    d = k.rolling(d_period).mean()
    return k, d


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range."""
    high, low, prev_close = df["high"], df["low"], df["close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period).mean()


# ── enrichment ────────────────────────────────────────────────────────────────

def enrich(df: pd.DataFrame, config) -> pd.DataFrame:
    """Add all indicator columns to the OHLCV DataFrame."""
    df = df.copy()
    close = df["close"]

    # RSI
    df["rsi"] = calculate_rsi(close, period=config.RSI_PERIOD)

    # EMA
    df[f"ema{config.EMA_SHORT}"]  = _ema(close, config.EMA_SHORT)
    df[f"ema{config.EMA_MEDIUM}"] = _ema(close, config.EMA_MEDIUM)
    df[f"ema{config.EMA_LONG}"]   = _ema(close, config.EMA_LONG)

    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(close)

    # Bollinger Bands
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = calculate_bollinger(close)

    # Stochastic RSI
    df["stoch_k"], df["stoch_d"] = calculate_stoch_rsi(close)

    # ATR
    df["atr"] = calculate_atr(df, period=config.RSI_PERIOD)

    # Volume SMA (20-period average volume)
    df["vol_sma"] = df["volume"].rolling(20).mean()

    return df


# ── scoring ───────────────────────────────────────────────────────────────────

def _score_signal(curr, prev, direction: str, config) -> dict:
    """
    Score a signal on a 0–10 scale.  Each check contributes 1–2 points.
    `direction` is "BUY" or "SELL".
    """
    is_buy = direction == "BUY"
    score = 0
    votes = []

    # 1. RSI cross (primary trigger, 2 pts)
    rsi_cross_up   = prev["rsi"] < config.RSI_OVERSOLD  and curr["rsi"] >= config.RSI_OVERSOLD
    rsi_cross_down = prev["rsi"] > config.RSI_OVERBOUGHT and curr["rsi"] <= config.RSI_OVERBOUGHT
    if (is_buy and rsi_cross_up) or (not is_buy and rsi_cross_down):
        score += 2
        votes.append("RSI cross ✅")
    else:
        votes.append("RSI cross ❌")

    # 2. EMA alignment (1 pt)
    ema_bull = curr[f"ema{config.EMA_SHORT}"] > curr[f"ema{config.EMA_MEDIUM}"]
    if (is_buy and ema_bull) or (not is_buy and not ema_bull):
        score += 1
        votes.append("EMA align ✅")
    else:
        votes.append("EMA align ❌")

    # 3. Price vs EMA50 (1 pt)
    above_ema50 = curr["close"] > curr[f"ema{config.EMA_LONG}"]
    if (is_buy and above_ema50) or (not is_buy and not above_ema50):
        score += 1
        votes.append("EMA50 side ✅")
    else:
        votes.append("EMA50 side ❌")

    # 4. MACD histogram direction (1 pt)
    macd_bull = curr["macd_hist"] > 0
    if (is_buy and macd_bull) or (not is_buy and not macd_bull):
        score += 1
        votes.append("MACD ✅")
    else:
        votes.append("MACD ❌")

    # 5. MACD cross (signal line cross, 1 pt)
    macd_cross_up   = prev["macd"] < prev["macd_signal"] and curr["macd"] >= curr["macd_signal"]
    macd_cross_down = prev["macd"] > prev["macd_signal"] and curr["macd"] <= curr["macd_signal"]
    if (is_buy and macd_cross_up) or (not is_buy and macd_cross_down):
        score += 1
        votes.append("MACD cross ✅")
    else:
        votes.append("MACD cross ❌")

    # 6. Bollinger Band position (1 pt)
    bb_oversold    = curr["close"] <= curr["bb_lower"]
    bb_overbought  = curr["close"] >= curr["bb_upper"]
    if (is_buy and bb_oversold) or (not is_buy and bb_overbought):
        score += 1
        votes.append("Bollinger ✅")
    else:
        votes.append("Bollinger ❌")

    # 7. Stochastic RSI (1 pt)
    stoch_bull = curr["stoch_k"] < 20 and curr["stoch_k"] > curr["stoch_d"]
    stoch_bear = curr["stoch_k"] > 80 and curr["stoch_k"] < curr["stoch_d"]
    if (is_buy and stoch_bull) or (not is_buy and stoch_bear):
        score += 1
        votes.append("Stoch RSI ✅")
    else:
        votes.append("Stoch RSI ❌")

    # 8. Volume confirmation (1 pt)
    high_volume = curr["volume"] > curr["vol_sma"]
    if high_volume:
        score += 1
        votes.append("Volume ✅")
    else:
        votes.append("Volume ❌")

    # Clamp to 10
    score = min(score, 10)

    if score >= 8:
        confidence = "Very High 🔥"
    elif score >= 6:
        confidence = "High 💪"
    elif score >= 4:
        confidence = "Medium ⚡"
    else:
        confidence = "Low ⚠️"

    return {"score": score, "confidence": confidence, "votes": votes}


# ── signal generation ─────────────────────────────────────────────────────────

def generate_signal(df: pd.DataFrame, config) -> dict | None:
    """
    Evaluate the latest candle and return a rich signal dict or None.
    Signals with score < MIN_SCORE are suppressed.
    """
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    rsi_now  = curr["rsi"]
    rsi_prev = prev["rsi"]
    ema_s    = curr[f"ema{config.EMA_SHORT}"]
    ema_m    = curr[f"ema{config.EMA_MEDIUM}"]
    ema_l    = curr[f"ema{config.EMA_LONG}"]
    entry    = curr["close"]
    atr      = curr["atr"]

    bullish_ema = ema_s > ema_m
    bearish_ema = ema_s < ema_m

    rsi_cross_up   = rsi_prev < config.RSI_OVERSOLD  and rsi_now >= config.RSI_OVERSOLD
    rsi_cross_down = rsi_prev > config.RSI_OVERBOUGHT and rsi_now <= config.RSI_OVERBOUGHT

    if rsi_cross_up and bullish_ema:
        direction = "BUY"
        direction_label = "BUY 🟢"
        stop_loss    = entry - atr * 1.5
        target1      = entry + atr * 1.0
        target2      = entry + atr * 2.0
        target3      = entry + atr * 3.0
    elif rsi_cross_down and bearish_ema:
        direction = "SELL"
        direction_label = "SELL 🔴"
        stop_loss    = entry + atr * 1.5
        target1      = entry - atr * 1.0
        target2      = entry - atr * 2.0
        target3      = entry - atr * 3.0
    else:
        return None

    exit_point   = stop_loss
    profit_limit = target3

    scoring = _score_signal(curr, prev, direction, config)

    # Suppress weak signals
    if scoring["score"] < config.MIN_SIGNAL_SCORE:
        return None

    return {
        "direction":        direction_label,
        "raw_direction":    direction,
        "rsi":              round(rsi_now, 2),
        "ema_short":        ema_s,
        "ema_medium":       ema_m,
        "ema_long":         ema_l,
        "macd":             round(curr["macd"], 4),
        "macd_signal":      round(curr["macd_signal"], 4),
        "stoch_k":          round(curr["stoch_k"], 1),
        "stoch_d":          round(curr["stoch_d"], 1),
        "atr":              atr,
        # trading levels
        "entry":        entry,
        "exit":         exit_point,
        "target1":      target1,
        "target2":      target2,
        "target3":      target3,
        "stop_loss":    stop_loss,
        "profit_limit": profit_limit,
        # formatted strings
        "entry_fmt":        _fmt(entry),
        "exit_fmt":         _fmt(exit_point),
        "target1_fmt":      _fmt(target1),
        "target2_fmt":      _fmt(target2),
        "target3_fmt":      _fmt(target3),
        "stop_loss_fmt":    _fmt(stop_loss),
        "profit_limit_fmt": _fmt(profit_limit),
        # scoring
        "score":        scoring["score"],
        "confidence":   scoring["confidence"],
        "votes":        scoring["votes"],
    }
