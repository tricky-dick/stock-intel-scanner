import time
from datetime import datetime

import yfinance as yf
from rich.console import Console
from rich.table import Table


console = Console()


def load_watchlist(file_path="watchlist.txt"):
    with open(file_path, "r") as file:
        return [line.strip().upper() for line in file if line.strip()]


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="2d")

    if history.empty or len(history) < 2:
        return None

    previous_close = history["Close"].iloc[-2]
    latest_close = history["Close"].iloc[-1]
    latest_volume = int(history["Volume"].iloc[-1])

    change_percent = ((latest_close - previous_close) / previous_close) * 100

    return {
        "ticker": ticker,
        "price": latest_close,
        "change_percent": change_percent,
        "volume": latest_volume,
    }


def build_table(results):
    table = Table(title="Stock Intel Scanner")

    table.add_column("Ticker", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("Change %", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Alert", justify="left")

    for item in results:
        alert = "NORMAL"

        if item["volume"] > 100_000_000:
            alert = "HIGH VOLUME"

        if item["change_percent"] > 5:
            alert = "MOMENTUM"

        table.add_row(
            item["ticker"],
            f"${item['price']:.2f}",
            f"{item['change_percent']:.2f}%",
            f"{item['volume']:,}",
            alert,
        )

    return table


def main():
    tickers = load_watchlist()
    results = []

    console.clear()
    console.print("=" * 60)
    console.print("[bold]STOCK INTEL SCANNER[/bold]")
    console.print(f"Updated: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    console.print("=" * 60)

    for ticker in tickers:
        console.print(f"Loading {ticker}...")
        data = get_stock_data(ticker)

        if data:
            results.append(data)
        else:
            console.print(f"[red]Could not load data for {ticker}[/red]")

        time.sleep(0.25)

    console.clear()
    console.print(f"[bold]Updated:[/bold] {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    console.print(build_table(results))


if __name__ == "__main__":
    main()
