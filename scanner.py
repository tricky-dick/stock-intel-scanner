import json
import time
from datetime import datetime

import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


def load_watchlist(file_path="watchlist.txt"):
    with open(file_path, "r") as file:
        return [line.strip().upper() for line in file if line.strip()]


def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        return json.load(file)


def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()

    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    latest_rsi = rsi.iloc[-1]

    if latest_rsi != latest_rsi:
        return None

    return latest_rsi


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="1mo")

    if history.empty or len(history) < 15:
        return None

    previous_close = history["Close"].iloc[-2]
    latest_close = history["Close"].iloc[-1]
    latest_volume = int(history["Volume"].iloc[-1])
    rsi = calculate_rsi(history["Close"])

    change_percent = ((latest_close - previous_close) / previous_close) * 100

    return {
        "ticker": ticker,
        "price": latest_close,
        "change_percent": change_percent,
        "volume": latest_volume,
        "rsi": rsi,
    }


def calculate_score(stock, config):
    score = 0
    scoring = config["scoring"]

    if stock["price"] < config["max_price"]:
        score += scoring["price_under_max"]

    if stock["volume"] > config["min_volume"]:
        score += scoring["volume_over_min"]

    if stock["change_percent"] > 0:
        score += scoring["positive_change"]

    if stock["change_percent"] > 5:
        score += 20

    if stock["rsi"] is not None:
        if stock["rsi"] < 30:
            score += 15
        elif 40 <= stock["rsi"] <= 65:
            score += 10
        elif stock["rsi"] > 70:
            score -= 10

    return score


def get_alert(stock):
    if stock["rsi"] is not None and stock["rsi"] < 30:
        return "OVERSOLD"

    if stock["rsi"] is not None and stock["rsi"] > 70:
        return "OVERBOUGHT"

    if stock["score"] >= 70:
        return "STRONG WATCH"

    if stock["score"] >= 50:
        return "WATCH"

    if stock["volume"] > 100_000_000:
        return "HIGH VOLUME"

    if stock["change_percent"] > 5:
        return "MOMENTUM"

    if stock["change_percent"] < -5:
        return "SELLING OFF"

    return "NORMAL"


def build_table(results):
    table = Table(title="Stock Intel Scanner")

    table.add_column("Ticker", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("Change %", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("RSI", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Alert", justify="left")

    for item in results:
        rsi_display = "N/A" if item["rsi"] is None else f"{item['rsi']:.2f}"

        table.add_row(
            item["ticker"],
            f"${item['price']:.2f}",
            f"{item['change_percent']:.2f}%",
            f"{item['volume']:,}",
            rsi_display,
            str(item["score"]),
            item["alert"],
        )

    return table


def run_scan():
    config = load_config()
    tickers = load_watchlist()
    results = []
    log_lines = []

    for ticker in tickers:
        log_lines.append(f"Loading {ticker}...")
        data = get_stock_data(ticker)

        if data:
            data["score"] = calculate_score(data, config)
            data["alert"] = get_alert(data)
            results.append(data)
            rsi_display = "N/A" if data["rsi"] is None else f"{data['rsi']:.2f}"
            log_lines.append(f"{ticker} loaded. RSI: {rsi_display}. Score: {data['score']}")
        else:
            log_lines.append(f"Could not load data for {ticker}")

        time.sleep(0.25)

    results.sort(key=lambda stock: stock["score"], reverse=True)

    return results, log_lines, config


def main():
    try:
        while True:
            results, log_lines, config = run_scan()

            console.clear()
            console.print(f"[bold]Updated:[/bold] {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
            console.print(build_table(results))

            scanner_log = "\n".join(log_lines[-10:])
            console.print(Panel(scanner_log, title="Scanner Log"))

            refresh_seconds = config.get("refresh_seconds", 60)
            console.print(f"[dim]Refreshing again in {refresh_seconds} seconds. Press CTRL+C to stop.[/dim]")

            time.sleep(refresh_seconds)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Scanner stopped by user.[/bold yellow]")


if __name__ == "__main__":
    main()
