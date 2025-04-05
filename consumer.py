from kafka import KafkaConsumer
import json
import pandas as pd
import psycopg2
from datetime import datetime
import os

from config import TICKERS

# Kafka setup
consumer = KafkaConsumer(
    'stock_prices', # Kafka topic this consumer is subscribing to.
    bootstrap_servers = "localhost:9092", # Address of the Kafka broker
    value_deserializer = lambda m: json.loads(m.decode('utf-8')), # byte ➜ JSON ➜ Python dict
    auto_offset_reset = 'earliest', # Get all existing messages if it’s the first time this group connects
    enable_auto_commit = True, # Kafka remembers where you left off, so you don’t read duplicates
    group_id = 'stock-group' # Lets multiple consumers share the load of processing messages
)


# PostgreSQL setup
conn = psycopg2.connect(
    dbname = 'stockdb',
    user = 'stockuser',
    password = 'stockpass',
    host = 'localhost',
    port = '5432'
)
cur = conn.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    ticker TEXT,
    price FLOAT,
    high FLOAT,
    low FLOAT,
    open FLOAT,
    prev_close FLOAT,
    timestamp TIMESTAMP
)
""")
conn.commit() # This tells the PostgreSQL database to save all changes made by your current SQL commands


# Parquet setup
save_dir = "parquet_data" # Holds the name of the directory where you will save your .parquet files.
os.makedirs(save_dir, exist_ok=True) # Creates the directory named "parquet_data" if it doesn't already exist
buffer = [] # Creates an empty list to temporarily hold incoming data records from Kafka. Batch multiple records in memory using this buffer
batch_size = 20
print("🔄 Listening to Kafka topic: stock_prices ...\n")


# Infinite loop — waits for new messages from the Kafka topic.
for message in consumer:
    data = message.value # Gets the actual content of the message
    print(f"[Kafka]] Received: {data}")

    # Insert one stock record into PostgreSQL
    cur.execute("""
    INSERT INTO stock_prices (ticker, price, high, low, open, prev_close, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data['ticker'], data['price'], data['high'], data['low'],
    data['open'], data['prev_close'], data['timestamp']))
    conn.commit() # The above put in buffer, then this line save the content in buffer to database.


    # Insert data into Parquet
    buffer.append(data)
    if len(buffer) >= batch_size:
        df = pd.DataFrame(buffer)

        safe_time = datetime.now().strftime("%Y%m%d_%H%M%S") # Generates a safe, timestamped filename, so each file is unique. Example output: "20250404_154523"
        filename = f"{save_dir}/stock_{safe_time}.parquet" # parquet_data/stock_20250404_154523.parquet

        df.to_parquet(filename, index=False)
        print(f"✅ Saved {len(buffer)} records to {filename}")
        buffer = [] # Reset buffer after the process