# modules/stocks.py

import requests

_last_known = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_stock_summary(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        response = requests.get(url, headers=HEADERS, timeout=5)
        result = response.json()

        if result["chart"]["error"] or not result["chart"]["result"]:
            raise Exception("Yahoo returned error or empty result")

        meta = result["chart"]["result"][0]["meta"]
        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]

        change = price - prev
        pct = (change / prev) * 100
        arrow = "↑" if change > 0 else "↓" if change < 0 else "-"

        _last_known[symbol] = (price, change, pct, arrow)

        return f"{symbol:<4}: {price:>6.2f} {arrow} {pct:+6.2f}%"

    except Exception:
        fallback = _last_known.get(symbol)
        if fallback:
            price, change, pct, arrow = fallback
            return f"{symbol:<4}: {price:>6.2f} {arrow} {pct:+6.2f}%"
        return f"{symbol:<4}:   N/A"

