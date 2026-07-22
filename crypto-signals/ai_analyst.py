"""
Ultra-Advanced AI signal analyst powered by Google Gemini.
Now fully Persian output.

Adds:
- Probability estimation
- Risk scoring
- Trend evaluation
- Smart emoji system
- Deep multi-layer reasoning (Persian)
"""

import os
import logging

from google import genai
from google.genai import types

log = logging.getLogger(__name__)

_MODEL_NAME = "gemini-2.0-flash"
_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def analyse(symbol: str, interval: str, signal: dict) -> dict:
    """
    Ultra-advanced Persian AI analysis:
      - Probability of success
      - Risk score
      - Trend strength
      - Smart emojis
      - Deep reasoning (Persian)
    """
    s = signal
    direction = s["raw_direction"]

    prompt = f"""
تو یک تحلیل‌گر ارشد بازار کریپتو با بیش از ۱۰ سال تجربه هستی.
لطفاً یک تحلیل چندلایه، دقیق و کاملاً فارسی از این سیگنال {direction} برای {symbol} در تایم‌فریم {interval} ارائه بده.

وظایف تو:
1. قدرت روند را ارزیابی کن (ضعیف / متوسط / قوی).
2. تأیید مومنتوم را بررسی کن.
3. احتمال موفقیت معامله را تخمین بزن (۰ تا ۱۰۰٪).
4. سطح ریسک را مشخص کن (کم / متوسط / زیاد).
5. یک تحلیل ۲–۳ جمله‌ای عمیق ارائه بده.
6. در نهایت یک نتیجه‌گیری بده: STRONG / MODERATE / WEAK / SKIP.

== داده‌های اندیکاتورها ==
قیمت:        ${s['entry_fmt']}
RSI-14:       {s['rsi']}
MACD:         {s['macd']}  (سیگنال: {s['macd_signal']})
Stoch RSI K:  {s['stoch_k']}   D: {s['stoch_d']}
EMA7:         {s['ema_short']:.4f}
EMA14:        {s['ema_medium']:.4f}
EMA50:        {s['ema_long']:.4f}
ATR:          {s['atr']:.4f}

== سیستم امتیازدهی ==
امتیاز: {s['score']}/10  ({s['confidence']})
تأییدها: {', '.join(s['votes'])}

== سطوح معامله ==
ورود:        ${s['entry_fmt']}
حد ضرر:      ${s['stop_loss_fmt']}
هدف ۱:       ${s['target1_fmt']}
هدف ۲:       ${s['target2_fmt']}
هدف ۳:       ${s['target3_fmt']}

فقط و فقط در این قالب پاسخ بده:

VERDICT: <STRONG|MODERATE|WEAK|SKIP>
PROBABILITY: <0-100%>
RISK: <کم|متوسط|زیاد>
TREND: <ضعیف|متوسط|قوی>
ANALYSIS: <۲–۳ جمله تحلیل عمیق فارسی>
"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=_MODEL_NAME,
            contents=prompt,
        )
        text = response.text.strip()
        return _parse_response(text)
    except Exception as exc:
        log.warning("Gemini analysis failed: %s", exc)
        return {
            "ai_verdict": "UNKNOWN",
            "ai_summary": "تحلیل هوش مصنوعی در دسترس نیست.",
            "ai_emoji": "🤖",
            "ai_probability": "0%",
            "ai_risk": "نامشخص",
            "ai_trend": "نامشخص",
        }


def _parse_response(text: str) -> dict:
    verdict = "UNKNOWN"
    summary = "تحلیلی دریافت نشد."
    probability = "0%"
    risk = "نامشخص"
    trend = "نامشخص"

    for line in text.splitlines():
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip().upper()
        elif line.startswith("ANALYSIS:"):
            summary = line.replace("ANALYSIS:", "").strip()
        elif line.startswith("PROBABILITY:"):
            probability = line.replace("PROBABILITY:", "").strip()
        elif line.startswith("RISK:"):
            risk = line.replace("RISK:", "").strip()
        elif line.startswith("TREND:"):
            trend = line.replace("TREND:", "").strip()

    emoji_map = {
        "STRONG":   "🔥🚀",
        "MODERATE": "🟢📈",
        "WEAK":     "⚠️📉",
        "SKIP":     "🚫",
        "UNKNOWN":  "🤖",
    }

    return {
        "ai_verdict": verdict,
        "ai_summary": summary,
        "ai_emoji": emoji_map.get(verdict, "🤖"),
        "ai_probability": probability,
        "ai_risk": risk,
        "ai_trend": trend,
    }
