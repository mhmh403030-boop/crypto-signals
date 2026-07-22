"""
Telegram messenger: sends trading signal messages to a configured chat.
"""
import requests
import config

_BASE_URL = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"


def send_message(text: str) -> None:
    """Send a plain-text message (HTML formatted) to the Telegram chat."""
    url = f"{_BASE_URL}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram error: {result}")


def format_signal(symbol: str, signal: dict, interval: str, ai: dict | None = None) -> str:
    """Build a Persian HTML-formatted Telegram message for a trading signal."""
    s = signal
    votes_str = " | ".join(s["votes"])

    # AI block (Persian)
    ai_block = ""
    if ai:
        ai_block = (
            f"\n"
            f"🤖 <b>تحلیل هوش مصنوعی:</b> {ai['ai_emoji']} <b>{ai['ai_verdict']}</b>\n"
            f"🔹 <b>قدرت روند:</b> {ai['ai_trend']}\n"
            f"🔹 <b>احتمال موفقیت:</b> {ai['ai_probability']}\n"
            f"🔹 <b>سطح ریسک:</b> {ai['ai_risk']}\n"
            f"📝 <i>{ai['ai_summary']}</i>\n"
        )

    return (
        f"<b>📊 سیگنال جدید ({s['direction']})</b>\n"
        f"🔸 <b>جفت‌ارز:</b> {symbol}\n"
        f"🔸 <b>تایم‌فریم:</b> <code>{interval}</code>\n"
        f"\n"
        f"🧠 <b>قدرت سیگنال:</b> {s['confidence']}  (<b>{s['score']}/10</b>)\n"
        f"🔹 <i>{votes_str}</i>\n"
        f"{ai_block}"
        f"\n"
        f"💰 <b>سطوح معامله:</b>\n"
        f"• ورود: <code>${s['entry_fmt']}</code>\n"
        f"• حد ضرر: <code>${s['stop_loss_fmt']}</code>\n"
        f"• هدف ۱: <code>${s['target1_fmt']}</code>\n"
        f"• هدف ۲: <code>${s['target2_fmt']}</code>\n"
        f"• هدف ۳: <code>${s['target3_fmt']}</code>\n"
        f"\n"
        f"📉 <b>اندیکاتورها:</b>\n"
        f"<i>RSI: {s['rsi']} | MACD: {s['macd']} | StochRSI K: {s['stoch_k']}</i>"
    )


def send_startup_message() -> None:
    send_message(
        "🤖 <b>ربات سیگنال‌دهی کریپتو فعال شد</b>\n"
        f"نمادهای تحت نظر: {', '.join(config.SYMBOLS)}\n"
        f"تایم‌فریم: <code>{config.INTERVAL}</code>\n"
        f"RSI دوره: {config.RSI_PERIOD} | "
        f"اشباع فروش: {config.RSI_OVERSOLD} | اشباع خرید: {config.RSI_OVERBOUGHT}"
    )


def send_error(symbol: str, error: str) -> None:
    send_message(f"⚠️ <b>خطا در پردازش {symbol}</b>\n<code>{error}</code>")
