# Crypto Signals Bot

Fetches live OHLCV candlestick data from KuCoin, calculates **RSI** and **EMA** technical indicators, and sends **BUY / SELL** signals to a Telegram chat.

## Features

- **KuCoin public API** — no KuCoin account or API key needed
- **RSI (14)** — signals when price crosses oversold (30) or overbought (70) thresholds
- **EMA 9 / 21 / 50** — trend confirmation filter
- **Telegram notifications** — rich HTML-formatted messages
- **Scheduled loop** — re-runs every 60 minutes by default

## Signal Logic

| Signal | Condition |
|--------|-----------|
| 🟢 BUY  | RSI crosses **up** through 30 AND EMA9 > EMA21 |
| 🔴 SELL | RSI crosses **down** through 70 AND EMA9 < EMA21 |

## Setup

### 1. Install dependencies

```bash
cd crypto-signals
pip install -r requirements.txt
```

### 2. Set secrets

Set these via Replit Secrets (already done if you used the setup flow):

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Your chat/channel ID (get via [@userinfobot](https://t.me/userinfobot)) |

### 3. Run

```bash
# Run continuously (every 60 minutes)
python main.py

# Run a single analysis pass and exit
python main.py --once
```

## Configuration

Edit `config.py` to change:

| Setting | Default | Description |
|---------|---------|-------------|
| `SYMBOLS` | BTC, ETH, SOL, BNB, XRP | Trading pairs to monitor |
| `INTERVAL` | `1hour` | KuCoin candle interval |
| `RSI_PERIOD` | 14 | RSI lookback period |
| `RSI_OVERSOLD` | 30 | RSI buy threshold |
| `RSI_OVERBOUGHT` | 70 | RSI sell threshold |
| `EMA_SHORT/MEDIUM/LONG` | 9 / 21 / 50 | EMA periods |
| `CHECK_INTERVAL_MINUTES` | 60 | How often to run |

## Available KuCoin intervals

`1min`, `3min`, `5min`, `15min`, `30min`, `1hour`, `2hour`, `4hour`, `6hour`, `8hour`, `12hour`, `1day`, `1week`
