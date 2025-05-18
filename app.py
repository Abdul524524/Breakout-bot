import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
CHAT_ID = os.getenv("CHAT_ID")      # Telegram Chat ID

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.ok

def fetch_data(symbol: str, interval: str, lookback_days: int = 5):
    end = datetime.now()
    start = end - timedelta(days=lookback_days)
    df = yf.download(symbol, start=start, end=end, interval=interval)
    df.dropna(inplace=True)
    return df

def detect_breakout(df: pd.DataFrame, window: int = 20):
    df['high_trend'] = df['High'].rolling(window).max()
    df['low_trend'] = df['Low'].rolling(window).min()
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    breakout = None
    if previous['Close'] < previous['high_trend'] and latest['Close'] > latest['high_trend']:
        breakout = "Bullish breakout"
    elif previous['Close'] > previous['low_trend'] and latest['Close'] < latest['low_trend']:
        breakout = "Bearish breakout"

    return breakout, latest.name.strftime("%Y-%m-%d %H:%M")

def check_ndx_breakouts():
    timeframes = {
        "15m": "15m",
        "1H": "60m",
        "4H": "240m"
    }
    for label, interval in timeframes.items():
        df = fetch_data("^NDX", interval)
        breakout, timestamp = detect_breakout(df)
        if breakout:
            message = f"{breakout} detected on NASDAQ (^NDX)\nTimeframe: {label}\nTime: {timestamp}"
            print(message)
            send_telegram_message(message)

if __name__ == "__main__":
    while True:
        try:
            check_ndx_breakouts()
        except Exception as e:
            print("Error:", e)
        time.sleep(600)  # wait 10 minutes
