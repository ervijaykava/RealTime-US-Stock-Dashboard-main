
import json
import time
from datetime import datetime

import requests
import yfinance as yf


# Power BI connection
PUSH_URL = "https://api.powerbi.com/beta/acac6b4e-d802-46e9-ac63-f7724bdfdb83/datasets/f8479739-9017-4076-8b10-823a2867edb1/rows?experience=power-bi&key=bkR2m%2B6Y50ZWRsIDciXNH%2BYco9dhCA2RmBiMdeYD2rkUXOevg53On5C6yUZO7NC4ed7wu2PWX%2FeLnzsA%2F50K4g%3D%3D"

# Stock symbols
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


def get_stock_data(symbol):
    """Return the latest available price data for a stock."""
    history = yf.Ticker(symbol).history(
        period="1d",
        interval="1m"
    )

    if history.empty:
        print(f"No data available for {symbol}")
        return None

    latest = history.iloc[-1]

    return {
        "Symbol": symbol,
        "Price": round(float(latest["Close"]), 2),
        "High": round(float(latest["High"]), 2),
        "Low": round(float(latest["Low"]), 2),
        "Volume": int(latest["Volume"]),
        "EventTime": datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    }


def send_to_power_bi(rows):
    """Send stock data to the existing Power BI endpoint."""
    if not rows:
        print("No stock data to send")
        return

    response = requests.post(
        PUSH_URL,
        data=json.dumps(rows),
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    print(f"Power BI status: {response.status_code}")

    if not response.ok:
        print(f"Power BI response: {response.text[:300]}")


def main():
    """Fetch stock prices and send updates every 60 seconds."""
    print("Stock streaming started")

    while True:
        try:
            rows = []

            for symbol in STOCKS:
                try:
                    stock = get_stock_data(symbol)

                    if stock is not None:
                        rows.append(stock)
                        print(f"{symbol}: ${stock['Price']}")

                except Exception as error:
                    print(f"Failed to fetch {symbol}: {error}")

            send_to_power_bi(rows)

            print("Waiting 60 seconds...\n")
            time.sleep(60)

        except KeyboardInterrupt:
            print("Stock streaming stopped")
            break

        except (requests.RequestException, Exception) as error:
            print(f"Update error: {error}")
            time.sleep(10)


if __name__ == "__main__":
    main()
