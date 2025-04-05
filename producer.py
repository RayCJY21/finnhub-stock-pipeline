from kafka import KafkaProducer
import time
import json
from finnhub_fetcher import fetch_data, get_local_time
from config import TICKERS

TOPIC = "stock_prices"

producer = KafkaProducer(
    bootstrap_servers = 'localhost:9092',
    value_serializer = lambda v:json.dumps(v).encode('utf-8') #Python dict ➜ JSON ➜ UTF-8 bytes
)

def stream_to_kafka():
    while True:
        stock_data = fetch_data(TICKERS)
        now = get_local_time() # Get the local time from finnhub_fetcher and store in now

        for stock in stock_data:
            stock["timestamp"] = now # Put the local time as timestamp on the data
            try:
                producer.send(TOPIC, value=stock)
                print(f"[Kafka] Sent:{stock}")
            except Exception as e:
                print(f"❌ Kafka Send Failed: {e}")
        time.sleep(10)


if __name__ == "__main__":
    stream_to_kafka()