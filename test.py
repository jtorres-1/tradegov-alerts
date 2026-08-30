import requests
import json
import os
import time

BASE = "https://congressinfor-production.up.railway.app"
WATCHLIST = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD"]
SEEN_FILE = "seen_trades.json"

TOKEN = "8677567177:AAGnO3CulTiexahTOLe1z9wndDRe87j4nkk"
CHANNEL = "@tradegovalerts"

def check_for_new_trades():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            seen = set(json.load(f))
    else:
        seen = set()

    new_trades = []

    for ticker in WATCHLIST:
        r = requests.get(f"{BASE}/trades/{ticker}")
        data = r.json()
        for t in data["trades"]:
            trade_id = f"{t['member']}-{t['ticker']}-{t['tx_date']}-{t['amount']}"
            if trade_id not in seen:
                new_trades.append(t)
                seen.add(trade_id)

    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

    print(f"{len(new_trades)} new trades to alert")

    for t in new_trades:
        direction = t["trade_type"].upper()
        message = (
            f"NEW FILING\n"
            f"{t['member']} ({t['chamber']})\n"
            f"{direction} {t['ticker']}\n"
            f"Amount: {t['amount']}\n"
            f"Trade date: {t['tx_date']}\n"
            f"Disclosed: {t['disclosed']}"
        )
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        resp = requests.post(url, data={"chat_id": CHANNEL, "text": message})
        print(resp.status_code, t["member"], t["ticker"])

while True:
    check_for_new_trades()
    print("Sleeping 30 minutes...")
    time.sleep(1800)