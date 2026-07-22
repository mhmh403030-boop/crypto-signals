# Crypto Signals Bot

A Python bot that fetches live crypto price data from KuCoin, computes RSI and EMA indicators, and sends BUY/SELL signals to a Telegram chat.

## Run & Operate

- **Workflow**: `Crypto Signals Bot` — runs `cd crypto-signals && python main.py`
- **One-shot**: `cd crypto-signals && python main.py --once` — single analysis pass, then exit
- Required secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- No KuCoin credentials needed (uses public market data API)

## Stack

- Python 3.11
- `requests` — KuCoin & Telegram API calls
- `pandas` / `numpy` — OHLCV data processing and indicator math
- `schedule` — recurring analysis loop

## Where things live

```
crypto-signals/
├── main.py          # Entry point, scheduler, argument parsing
├── config.py        # All tunable settings (symbols, intervals, thresholds)
├── kucoin.py        # KuCoin REST API client (OHLCV fetching)
├── indicators.py    # RSI, EMA calculations + signal generation logic
├── telegram_bot.py  # Telegram message formatting and delivery
└── requirements.txt
```

## Architecture decisions

- **Signal logic**: BUY when RSI crosses up through 30 AND EMA9 > EMA21; SELL when RSI crosses down through 70 AND EMA9 < EMA21. Both conditions required to reduce false signals.
- **Public API only**: KuCoin's `/api/v1/market/candles` endpoint requires no authentication, keeping the setup frictionless.
- **Wilder's smoothing for RSI**: Uses EWM with `com=period-1` to match the standard Wilder RSI formula exactly.

## Configuration (crypto-signals/config.py)

| Setting | Default | Description |
|---------|---------|-------------|
| `SYMBOLS` | BTC/ETH/SOL/BNB/XRP | Pairs to monitor |
| `INTERVAL` | `1hour` | Candle interval |
| `RSI_PERIOD` | 14 | RSI lookback |
| `RSI_OVERSOLD` | 30 | Buy RSI threshold |
| `RSI_OVERBOUGHT` | 70 | Sell RSI threshold |
| `CHECK_INTERVAL_MINUTES` | 60 | Scheduler frequency |

## Gotchas

- After changing `config.py`, restart the `Crypto Signals Bot` workflow for changes to take effect.
- KuCoin returns candles newest-first; `kucoin.py` reverses them so row 0 is oldest.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details (for the Node.js side of this monorepo)
