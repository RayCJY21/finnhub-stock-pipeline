from finnhub_fetcher import fetch_data
import pandas as pd

# Give a list of tickers
tickers = ["AAPL", "TSLA", "MSFT", "GOOGL"]
# Use fetch_data function from finnhub_fetcher.py and input the list
data = fetch_data(tickers)
# Converts that list of dictionaries into a Pandas DataFrame
df = pd.DataFrame(data)

print(df)