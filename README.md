# Finnhub Realtime Stock Data Pipeline 

This project is a full data engineering pipeline that collects real-time US stock market data using the [Finnhub API](https://finnhub.io), processes it with Kafka, stores it in PostgreSQL, and schedules with Airflow.

---

## ✨ Features
- Realtime stock data ingestion from Finnhub
- Kafka producer/consumer streaming
- PostgreSQL database storage
- Parquet file backup
- Apache Airflow for automated scheduling

---

## 🚀 Quick Start

### 1. Clone the repo and setup venv
```bash
git clone <repo-url>
cd your-root-folder
python3 -m venv venv
source venv/bin/activate
```

### 2. Setup Kafka + PostgreSQL
- Use Docker Compose to run Kafka + PostgreSQL
```bash
cd finnhub-stock-pipeline
# Update docker-compose.yml (includes kafka + postgres)
docker compose up -d
```

### 3. Start producer and consumer
```bash
python producer.py
python consumer.py
```

### 4. Setup Airflow
```bash
cd airflow
mkdir -p dags logs plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.2/docker-compose.yaml'
docker compose up airflow-init
docker compose up -d
```

### 5. Add DAG in `airflow/dags/`
```python
# DAG file: finnhub_to_postgres_dag.py
# Use PythonOperator to fetch stock data and store into PostgreSQL
```

Go to http://localhost:8080 (Airflow UI) → enable DAG

---

## ⚠️ Notes
- PostgreSQL must be reachable from Docker/Airflow. On macOS, use `host.docker.internal`
