
import os
import time
import json
from datetime import datetime

import pandas as pd
import requests
import yfinance as yf


# Power BI connection
PUSH_URL = "https://api.powerbi.com/beta/e51a2db9-06e9-41e8-9ef2-6de0e13b50f1/datasets/4c3064a2-ad10-45af-8075-5ab5dd31bc4a/rows?experience=power-bi&key=1PAIO%2FVKvvCE4ACuMrE4zkiPYiXYLNOXKJMmpWIm0W2veLD%2BISxWbwlW8WlXb4SyTbVDGXNGXNQMT4e1JxVtzA%3D%3D"

# Market symbols
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
INDICES = ["^GSPC", "^IXIC", "^DJI"]

# Keep existing file names unchanged
STOCK_CSV = "stock_data.csv"
INDEX_CSV = "index_data.csv"

INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "DOW JONES"
}


def get_time(value):
    """Convert a date to the existing timestamp format."""
    return pd.to_datetime(value).dt.strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )


def save_history(symbols, file_name, is_index=False):
    """Download and save one year of daily market data."""
    rows = []

    for symbol in symbols:
        try:
            history = yf.Ticker(symbol).history(
                period="1y",
                interval="1d"
            )

            if history.empty:
                print(f"No historical data for {symbol}")
                continue

            history = history.reset_index()

            history["Symbol"] = (
                INDEX_NAMES[symbol] if is_index else symbol
            )

            history["EventTime"] = get_time(history["Date"])
            history["Price"] = history["Close"].round(2)

            if is_index:
                rows.append(
                    history[["Symbol", "Price", "EventTime"]]
                )
            else:
                history["High"] = history["High"].round(2)
                history["Low"] = history["Low"].round(2)
                history["Open"] = history["Open"].round(2)
                history["Volume"] = history["Volume"].astype(int)

                rows.append(
                    history[
                        [
                            "Symbol", "Price", "High", "Low",
                            "Volume", "Open", "EventTime"
                        ]
                    ]
                )

            print(f"Loaded {symbol}: {len(history)} records")

        except Exception as error:
            print(f"Could not load {symbol}: {error}")

    if rows:
        pd.concat(rows, ignore_index=True).to_csv(
            file_name,
            index=False
        )
        print(f"Historical data saved to {file_name}")
    else:
        print(f"No data available for {file_name}")


def get_stock_metrics(symbol):
    """Calculate the latest price and market performance."""
    ticker = yf.Ticker(symbol)

    today = ticker.history(period="1d", interval="1m")
    week = ticker.history(period="5d", interval="1d")
    year = ticker.history(period="1y", interval="1d")

    if today.empty or week.empty or year.empty:
        print(f"Incomplete market data for {symbol}")
        return None

    price = round(float(today["Close"].iloc[-1]), 2)
    opening = round(float(today["Open"].iloc[0]), 2)
    high = round(float(today["High"].max()), 2)
    low = round(float(today["Low"].min()), 2)
    volume = int(today["Volume"].sum())

    week_open = float(week["Open"].iloc[0])

    if opening == 0 or week_open == 0:
        print(f"Invalid opening price for {symbol}")
        return None

    daily_change = round(
        ((price - opening) / opening) * 100, 2
    )

    weekly_change = round(
        ((price - week_open) / week_open) * 100, 2
    )

    daily_range = (
        (year["High"] - year["Low"]) / year["Low"]
    ) * 100

    daily_range = daily_range.replace(
        [float("inf"), float("-inf")], float("nan")
    ).dropna()

    volatility = (
        round(float(daily_range.mean()), 2)
        if not daily_range.empty else 0
    )

    return {
        "Symbol": symbol,
        "Price": price,
        "Open": opening,
        "High": high,
        "Low": low,
        "Volume": volume,
        "PriceChangePct": daily_change,
        "WeekChangePct": weekly_change,
        "Week52High": round(float(year["High"].max()), 2),
        "Week52Low": round(float(year["Low"].min()), 2),
        "Volatility": volatility,
        "EventTime": datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    }


def get_index_data():
    """Fetch the latest available index prices."""
    rows = []

    for symbol in INDICES:
        try:
            history = yf.Ticker(symbol).history(
                period="1d",
                interval="1m"
            )

            if history.empty:
                print(f"No current data for {symbol}")
                continue

            opening = float(history["Open"].iloc[0])
            price = round(float(history["Close"].iloc[-1]), 2)

            if opening == 0:
                continue

            change = round(
                ((price - opening) / opening) * 100, 2
            )

            rows.append({
                "Index": INDEX_NAMES[symbol],
                "Price": price,
                "ChangePct": change,
                "EventTime": datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z"
                )
            })

            print(
                f"{INDEX_NAMES[symbol]}: {price} "
                f"({change}%)"
            )

        except Exception as error:
            print(f"Index fetch failed for {symbol}: {error}")

    return rows


def update_market_data():
    """Fetch live prices, save files and update Power BI."""
    stock_rows = []
    metric_rows = []

    for symbol in STOCKS:
        try:
            metrics = get_stock_metrics(symbol)

            if metrics is None:
                continue

            stock_rows.append({
                "Symbol": metrics["Symbol"],
                "Price": metrics["Price"],
                "High": metrics["High"],
                "Low": metrics["Low"],
                "Volume": metrics["Volume"],
                "Open": metrics["Open"],
                "EventTime": metrics["EventTime"]
            })

            metric_rows.append(metrics)

            print(
                f"{symbol}: ${metrics['Price']} | "
                f"Day: {metrics['PriceChangePct']}% | "
                f"Week: {metrics['WeekChangePct']}%"
            )

        except Exception as error:
            print(f"Stock update failed for {symbol}: {error}")

    # Append new prices without replacing historical records
    if stock_rows:
        pd.DataFrame(stock_rows).to_csv(
            STOCK_CSV,
            mode="a",
            header=not os.path.exists(STOCK_CSV)
            or os.path.getsize(STOCK_CSV) == 0,
            index=False
        )

    # Keep only the latest metrics in this file
    pd.DataFrame(metric_rows).to_csv(
        "metrics_data.csv",
        index=False
    )

    # Save the latest index snapshot
    index_rows = get_index_data()

    pd.DataFrame(
        index_rows,
        columns=["Index", "Price", "ChangePct", "EventTime"]
    ).to_csv("live_index.csv", index=False)

    # Send stock rows using the existing Power BI API format
    if stock_rows:
        try:
            response = requests.post(
                PUSH_URL,
                data=json.dumps(stock_rows),
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            print(f"Power BI status: {response.status_code}")

            if not response.ok:
                print(f"Power BI response: {response.text[:300]}")

        except requests.RequestException as error:
            print(f"Power BI request failed: {error}")
    else:
        print("No stock rows available to send to Power BI")


def main():
    """Prepare historical data and start live updates."""
    print("Stock Market Pipeline Starting")
    print("-" * 40)

    if not os.path.exists(STOCK_CSV):
        save_history(STOCKS, STOCK_CSV)
    else:
        print(f"Using existing file: {STOCK_CSV}")

    if not os.path.exists(INDEX_CSV):
        save_history(INDICES, INDEX_CSV, is_index=True)
    else:
        print(f"Using existing file: {INDEX_CSV}")

    print("Live market updates started")

    while True:
        try:
            update_market_data()
            print("Next update in 60 seconds\n")
            time.sleep(60)

        except KeyboardInterrupt:
            print("Pipeline stopped")
            break

        except Exception as error:
            print(f"Update failed: {error}")
            time.sleep(10)


if __name__ == "__main__":
    main()
