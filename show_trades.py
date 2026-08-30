import requests

BASE = "https://congressinfor-production.up.railway.app"
TICKERS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD",
           "JPM", "LMT", "PYPL", "DIS"]

all_trades = []
for t in TICKERS:
    r = requests.get(f"{BASE}/trades/{t}", timeout=15)
    data = r.json()
    all_trades.extend(data.get("trades", []))

all_trades.sort(key=lambda x: x["tx_date"], reverse=True)
print(f"Total real trades pulled: {len(all_trades)}\n")
for t in all_trades[:15]:
    print(f"{t['member']} | {t['ticker']} | {t['trade_type']} | {t['amount']} | {t['tx_date']}")
