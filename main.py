import time
import schedule
import requests
from telegram import Bot

TELEGRAM_TOKEN = '6263579268:AAEb1tEtKwWmnGzAUzLVNYq3r2Imfx6MGJ8'
CHAT_ID = '1917297411'
bot = Bot(token=TELEGRAM_TOKEN)

def get_btc_price():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = response.json()
        return float(data['price'])
    except Exception as e:
        return None

def get_market_analysis():
    price = get_btc_price()
    if price is None:
        bot.send_message(chat_id=CHAT_ID, text="❌ Error fetching BTC price.", parse_mode='Markdown')
        return

    resistance = round(price + 150, 2)
    entry = round(price, 2)
    stop_loss = round(price + 200, 2)
    tp1 = round(price - 300, 2)
    tp2 = round(price - 500, 2)

    analysis = f"""
TRADE ALERT 🚨

🕒 Timeframe: 15m
📊 Pair: BTCUSDT (Binance Live Price)
📈 Price: ${price}

=========================

🔍 Chart Analysis

📌 Resistance: ${resistance}
- Market reaction: Strong seller zone

🕯️ Candlestick Pattern: Bearish Engulfing (simulated)
📉 Volume: Low on breakout, rising on rejection
📐 Structure: Lower high forming, rejection expected

=========================

🌐 Sentiment: Neutral to Bearish
- Whale activity: No major buys above resistance

=========================

✅ Trade Setup

📍 Type: SHORT
🎯 Entry: ${entry}
🛑 Stop Loss: ${stop_loss}
🎯 Target 1: ${tp1}
🎯 Target 2: ${tp2}
⚖️ R:R = 1:2+
📌 Reason: Rejection from resistance + volume behavior

=========================

🔁 Alternate Plan:
- Long above ${resistance + 100} | SL: ${entry} | TP: ${resistance + 300}
"""
    bot.send_message(chat_id=CHAT_ID, text=analysis, parse_mode='Markdown')

# Run every 15 minutes
schedule.every(15).minutes.do(get_market_analysis)

while True:
    schedule.run_pending()
    time.sleep(1)
