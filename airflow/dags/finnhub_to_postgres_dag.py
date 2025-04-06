from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import psycopg2

# DAG
default_args = {
    'owner': 'ray',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# 可自行擴充
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
FINNHUB_API_KEY = "cvn2irhr01ql90q14680cvn2irhr01ql90q1468g"  # Change to your api code

POSTGRES_CONN = {
    'dbname': 'stockdb',
    'user': 'stockuser',
    'password': 'stockpass',
    'host': 'host.docker.internal',  # or postgreSQL container
    'port': 5432
}

def fetch_and_save():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📡 [{now}] Fetching data...")

    data = []
    for ticker in TICKERS:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
            r = requests.get(url)
            q = r.json()
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
            print(f"❌ {ticker} fetch error: {e}")

    conn = psycopg2.connect(**POSTGRES_CONN)
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
    for row in data:
        cur.execute("""
            INSERT INTO stock_prices (ticker, price, high, low, open, prev_close, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['ticker'], row['price'], row['high'], row['low'],
            row['open'], row['prev_close'], row['timestamp']
        ))
    conn.commit()
    conn.close()
    print(f"✅ Saved {len(data)} rows to PostgreSQL")

with DAG(
    dag_id="finnhub_to_postgres",
    default_args=default_args,
    start_date=datetime(2025, 4, 6),
    schedule_interval="*/5 * * * *",
    catchup=False,
    tags=["stock"]
) as dag:
    task = PythonOperator(
        task_id="fetch_stock_data",
        python_callable=fetch_and_save
    )
