"""
Crypto Signals Bot
==================
Fetches OHLCV data from KuCoin, computes RSI and EMA indicators,
and sends BUY / SELL signals to a Telegram chat.

Usage:
    python main.py            # Run once immediately, then loop on schedule
    python main.py --once     # Run a single analysis pass and exit
"""
import argparse
import logging
import os
import sys
import time
import threading

import schedule

import config
import kucoin
import indicators
import telegram_bot
import ai_analyst
import server       # فایل Flask
import pinger       # ← پینگر داخلی

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def analyse_all() -> None:
    """Analyse every configured symbol and dispatch Telegram signals."""
    log.info("Running analysis for %d symbols…", len(config.SYMBOLS))
    signals_sent = 0

    for symbol in config.SYMBOLS:
        try:
            df = kucoin.fetch_candles(symbol)
            df = indicators.enrich(df, config)
            signal = indicators.generate_signal(df, config)

            if signal:
                ai = ai_analyst.analyse(symbol, config.INTERVAL, signal)
                log.info("AI verdict for %s: %s", symbol, ai["ai_verdict"])
                msg = telegram_bot.format_signal(symbol, signal, config.INTERVAL, ai)
                telegram_bot.send_message(msg)
                log.info("Signal sent for %s: %s", symbol, signal["direction"])
                signals_sent += 1
            else:
                log.info("%s — no actionable signal (RSI: %.1f)", symbol, df.iloc[-1]["rsi"])

        except Exception as exc:
            log.error("Error processing %s: %s", symbol, exc)
            try:
                telegram_bot.send_error(symbol, str(exc))
            except Exception as tg_exc:
                log.error("Failed to send error to Telegram: %s", tg_exc)

    log.info("Analysis complete. Signals sent: %d/%d", signals_sent, len(config.SYMBOLS))


def validate_config() -> bool:
    """Check that required env vars are present before starting."""
    ok = True
    if not config.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_TOKEN is not set.")
        ok = False
    if not config.TELEGRAM_CHAT_ID:
        log.error("TELEGRAM_CHAT_ID is not set.")
        ok = False
    return ok


def run_flask_server():
    """Run Flask server in background thread."""
    port = int(os.environ.get("PORT", 8080))
    server.app.run(host="0.0.0.0", port=port)


def main() -> None:
    # Start Flask server in background
    threading.Thread(target=run_flask_server, daemon=True).start()
    log.info("Flask keep-alive server started on port 8080")

    # Start internal
