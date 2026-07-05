import time
from datetime import datetime


def load_watchlist(file_path="watchlist.txt"):
    with open(file_path, "r") as file:
        tickers = [line.strip().upper() for line in file if line.strip()]
    return tickers


def main():
    tickers = load_watchlist()

    print("=" * 50)
    print("STOCK INTEL SCANNER")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    print()
    print("Loaded watchlist:")
    print("-" * 50)

    for ticker in tickers:
        print(f"Watching: {ticker}")
        time.sleep(0.25)

    print("-" * 50)
    print("Scanner test complete.")
    print("Next step: pull real stock data.")


if __name__ == "__main__":
    main()
