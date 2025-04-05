import finnhub
import os
from datetime import datetime
from dotenv import load_dotenv
import pytz
"""
finnhub: Official client SDK to interact with the Finnhub API.
os: Used to get environment variables (like your API key).
datetime: To get the current UTC time for timestamping the data.
load_dotenv: Loads variables from a .env file into your environment — so secrets like your API key are not hardcoded.
pytz: change to locate datetime
"""


# Load API securely
load_dotenv()
api_key = os.getenv("FINNHUB_API_KEY")
client = finnhub.Client(api_key=api_key)


def fetch_data(tickers):
    la_tz = pytz.timezone("America/Los_Angeles")
    now = datetime.now(la_tz).strftime("%Y-%m-%d %H:%M:%S")


    """
    Initializes an empty list to store results.
    Loops through each ticker and fetches live quote data using:
    """
    data = []
    for ticker in tickers:
        try:
            q = client.quote(ticker)
            data.append({
                "ticker": ticker,
                "price": q.get("c"),
                "high": q.get("h"),
                "low": q.get("l"),
                "open": q.get("o"),
                "prev_close": q.get("pc"),
                "timestamp": now
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return data