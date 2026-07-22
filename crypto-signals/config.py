import os

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# KuCoin API base URL (public — no credentials needed for market data)
KUCOIN_API_BASE = "https://api.kucoin.com"

# Trading pairs to monitor
SYMBOLS = [
    "BTC-USDT",
    "ETH-USDT",
    "SOL-USDT",
    "BNB-USDT",
    "XRP-USDT",
    "DOGE-USDT",
    "FARTCOIN-USDT",
    "ADA-USDT",
    "TRX-USDT",
]

# Candle interval
INTERVAL = "30min"

# Number of candles to fetch
CANDLE_LIMIT = 200

# RSI settings (more sensitive)
RSI_PERIOD = 14
RSI_OVERBOUGHT = 60   # was 70
RSI_OVERSOLD = 40     # was 30

# EMA periods (more sensitive)
EMA_SHORT = 7         # was 9
EMA_MEDIUM = 14       # was 21
EMA_LONG = 50

# How often to run the analysis (in minutes)
CHECK_INTERVAL_MINUTES = 30

# Minimum score required to send a signal (more signals)
MIN_SIGNAL_SCORE = 4   # stays 4, already good for fast signals
