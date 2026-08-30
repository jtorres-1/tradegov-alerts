import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE = "https://congressinfor-production.up.railway.app"
WATCHLIST = [
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD",
    "JPM", "BAC", "XOM", "CVX", "LMT", "RTX", "BA", "DIS",
    "NFLX", "CRM", "ORCL", "INTC", "PYPL", "V", "MA", "JNJ",
    "PFE", "MRNA", "WMT", "COST", "HD", "UNH", "T", "VZ"
]
SEEN_FILE = "seen_trades.json"
CURRENT_YEAR = datetime.now().year

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = "@tradegovalerts"


def size_tier(amount):
    # amount strings look like "$1,001 - $15,000" or "$100,001 -\n$250,000"
    a = amount.replace("\n", " ").replace(",", "")
    if "$1000001" in a or "$5000001" in a or "$25000001" in a or "$50000001" in a:
        return "WHALE TRADE"
    if "$500001" in a or "$250001" in a:
        return "MAJOR TRADE"
    if "$100001" in a:
        return "BIG TRADE"
    return None


def check_for_new_trades():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            seen = set(json.load(f))
    else:
        seen = set()

    new_trades = []

    for ticker in WATCHLIST:
        try:
            r = requests.get(f"{BASE}/trades/{ticker}", timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"API error for {ticker}: {e}")
            continue

        for t in data.get("trades", []):
            trade_id = f"{t['member']}-{t['ticker']}-{t['tx_date']}-{t['amount']}"
            if trade_id in seen:
                continue
            seen.add(trade_id)

            tx_year = t["tx_date"][:4]
            if tx_year != str(CURRENT_YEAR):
                continue  # mark seen but don't alert on stale/prior-year trades

            new_trades.append(t)

    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

    print(f"{len(new_trades)} new trades to alert")

    for t in new_trades:
        direction = t["trade_type"].upper()
        arrow = "BUY >>" if "BUY" in direction or "PURCHASE" in direction else "SELL <<"
        tier = size_tier(t["amount"])
        amount_clean = t["amount"].replace("\n", " ")

        lines = []
        if tier:
            lines.append(f"[{tier}]")
        lines.append("NEW FILING")
        lines.append(f"{t['member']} ({t['chamber']})")
        lines.append(f"{arrow} {t['ticker']}")
        lines.append(f"Amount: {amount_clean}")
        lines.append(f"Trade date: {t['tx_date']}")
        lines.append(f"Disclosed: {t['disclosed']}")
        message = "\n".join(lines)

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        try:
            resp = requests.post(url, data={"chat_id": CHANNEL, "text": message}, timeout=30)
            print(resp.status_code, t["member"], t["ticker"])
        except Exception as e:
            print(f"Telegram send error: {e}")
        time.sleep(1)  # avoid Telegram rate limits on burst sends


def main_loop():
    while True:
        check_for_new_trades()
        print("Sleeping 30 minutes...")
        time.sleep(1800)


main_loop()
