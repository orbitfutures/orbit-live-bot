import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import datetime
import schedule
import io
from telegram import Bot

# === CONFIG ===
TOKEN = "7397317010:AAE41dwNOzYF8pxsZiOITCdhULQ7GJpHcUY"
CHAT_ID = "1917297411"
PAIR = "btcusdt"
TIMEFRAME = "15m"
INTERVAL = 15  # minutes

# === FUNCTIONS ===

def fetch_candles(symbol=PAIR, interval=TIMEFRAME, limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    candles = [{
        "time": datetime.datetime.fromtimestamp(c[0] / 1000),
        "open": float(c[1]),
        "high": float(c[2]),
        "low": float(c[3]),
        "close": float(c[4]),
        "volume": float(c[5])
    } for c in data]
    return candles

def identify_levels(candles):
    highs = [c['high'] for c in candles[-20:]]
    lows = [c['low'] for c in candles[-20:]]
    resistance = max(highs)
    support = min(lows)
    return resistance, support

def detect_candle_pattern(candles):
    last = candles[-1]
    prev = candles[-2]
    if prev['close'] < prev['open'] and last['close'] > last['open'] and last['close'] > prev['open']:
        return "Bullish Engulfing"
    elif prev['close'] > prev['open'] and last['close'] < last['open'] and last['close'] < prev['open']:
        return "Bearish Engulfing"
    return "No pattern"

def generate_chart(candles, support, resistance):
    times = [c['time'] for c in candles]
    closes = [c['close'] for c in candles]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(times, closes, label="Close Price")
    ax.axhline(resistance, color='red', linestyle='--', label=f"Resistance: {resistance}")
    ax.axhline(support, color='green', linestyle='--', label=f"Support: {support}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.title("BTC/USDT - 15m")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def send_alert(bot, chart, text):
    bot.send_photo(chat_id=CHAT_ID, photo=chart, caption=text)

def create_message(candles, support, resistance, pattern, price):
    sentiment = "Bullish" if pattern == "Bullish Engulfing" else "Bearish" if pattern == "Bearish Engulfing" else "Neutral"
    setup = ""

    if price < resistance and pattern == "Bearish Engulfing":
        entry = price
        sl = resistance + 150
        tp1 = price - 300
        tp2 = price - 500
        setup = f"📍 Type: SHORT\n🎯 Entry: ${entry}\n🛑 SL: ${sl}\n🎯 TP1: ${tp1}\n🎯 TP2: ${tp2}\n⚖️ R:R = 1:2+"
        alt = f"🔁 Alternate:\nLong above ${resistance + 100} | SL: {entry} | TP: {resistance + 300}"
    elif price > support and pattern == "Bullish Engulfing":
        entry = price
        sl = support - 150
        tp1 = price + 300
        tp2 = price + 500
        setup = f"📍 Type: LONG\n🎯 Entry: ${entry}\n🛑 SL: ${sl}\n🎯 TP1: ${tp1}\n🎯 TP2: ${tp2}\n⚖️ R:R = 1:2+"
        alt = f"🔁 Alternate:\nShort below ${support - 100} | SL: {entry} | TP: {support - 300}"
    else:
        setup = "⚠️ No valid pattern detected. Waiting for confirmation."
        alt = "🔁 Monitor price near key S/R for breakout/rejection."

    msg = f"""
🚨 TRADE ALERT

🕒 Timeframe: 15m
📊 Pair: BTC/USDT (Binance)
📈 Price: ${price}

=========================

🔍 Chart Analysis

📌 Resistance: ${resistance}
📌 Support: ${support}
🕯️ Candlestick: {pattern}
🌐 Sentiment: {sentiment}

✅ Trade Setup
{setup}

{alt}
"""
    return msg

# === MAIN TASK ===

def run_analysis():
    try:
        print("📊 Running analysis...")
        bot = Bot(token=TOKEN)
        candles = fetch_candles()
        print("✅ Candles fetched:", len(candles))
        resistance, support = identify_levels(candles)
        pattern = detect_candle_pattern(candles)
        price = candles[-1]['close']
        chart = generate_chart(candles, support, resistance)
        message = create_message(candles, support, resistance, pattern, price)
        print("📤 Sending to Telegram...")
        send_alert(bot, chart, message)
    except Exception as e:
        print("❌ Error during analysis/send:", e)

# Run every 15 min
schedule.every(INTERVAL).minutes.do(run_analysis)

print("🤖 Bot started.")
run_analysis()

while True:
    schedule.run_pending()
    time.sleep(5)
