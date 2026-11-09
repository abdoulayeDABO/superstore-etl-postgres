# Superstore ETL Pipeline & Sales Dashboard

An end-to-end data project: a Python **ETL pipeline** loads the Superstore sales dataset into **PostgreSQL** (running in Docker), and an interactive **Streamlit** dashboard turns it into business insights.

## Objective

The goal of this project is to build a small but realistic data workflow, from raw file to dashboard:

- **Extract** raw sales data from a CSV file
- **Transform** it: standardize column names, parse dates, remove duplicates and invalid rows
- **Load** it into a PostgreSQL database in an idempotent way (the pipeline can be re-run safely)
- **Visualize** the results in an interactive dashboard with KPIs, trends and breakdowns

## Architecture

```
CSV file  -->  Extract  -->  Transform  -->  Load  -->  PostgreSQL (Docker)  -->  Streamlit dashboard
              (pandas)       (pandas)     (SQLAlchemy)                            (SQL queries + charts)
```

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.14 |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| Data processing | pandas |
| Database access | SQLAlchemy + psycopg2 |
| Database | PostgreSQL 16 |
| Containerization | Docker Compose |
| Configuration | python-dotenv (`.env`) |
| Dashboard | Streamlit |

## Project Structure

```
superstore-postgres-etl/
├── data/
│   ├── README.md                  # Dataset description
│   └── Sample - Superstore.csv    # Source data (not versioned)
├── screenshots/                   # Dashboard screenshots used in this README
├── .streamlit/
│   └── secrets.toml               # Streamlit DB connection (not versioned)
├── .env                           # Local configuration (not versioned)
├── .env.example                   # Template for the variables to define
├── compose.yml                    # PostgreSQL service
├── init.sql                       # Table and index creation
├── etl.py                         # ETL pipeline (extract, transform, load)
├── dashboard.py                   # Streamlit dashboard
├── pyproject.toml
└── uv.lock
```

## ETL Pipeline

**Extract**: reads `Sample - Superstore.csv` with pandas (`latin-1` encoding, postal codes kept as text to preserve leading zeros).

**Transform**:
- renames the columns to `snake_case`
- converts `order_date` and `ship_date` to `datetime`
- removes duplicates (ignoring the unique `row_id`)
- drops rows with missing critical values (`order_id`, `order_date`, `sales`)

**Load**: truncates the `orders` table and reloads the cleaned data in a single transaction, so re-running the pipeline never creates duplicates.

## Database Schema

A single `orders` table (`row_id` as primary key) with indexes on `order_id`, `order_date`, `customer_id` and `product_id`. See [`init.sql`](init.sql).

## Dashboard

### Key Performance Indicators

Six KPIs, each with an icon, a sparkline and a delta showing the change between the last two months of data: total orders, total sales, total profit, customers, average basket and profit margin.

![KPIs](screenshots/kpi.png)

### Monthly Trend

A line chart of sales, profit or orders over time, switchable with a selector.

![Monthly trend](screenshots/trend.png)

### Performance Breakdown

Sales and profit by region, and the top 10 products by sales.

![Performance breakdown](screenshots/performance.png)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/)
- The [Superstore dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) saved as `data/Sample - Superstore.csv`

### 1. Clone and install

```bash
git clone https://github.com/abdoulayeDABO/superstore-etl-postgres.git
cd superstore-postgres-etl
uv sync
```

### 2. Configure the environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default values:

```
PG_USERNAME=postgres
PG_PASSWORD=postgres
PG_DATABASE=superstore
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/superstore
```

Create `.streamlit/secrets.toml` for the dashboard connection:

```toml
[connections.postgresql]
dialect = "postgresql"
driver = "psycopg2"
host = "localhost"
port = 5432
database = "superstore"
username = "postgres"
password = "postgres"
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

The `orders` table is created automatically from `init.sql` on first start.

### 4. Run the ETL pipeline

```bash
uv run python etl.py
```

### 5. Launch the dashboard

```bash
uv run streamlit run dashboard.py
```

Then open http://localhost:8501.

### Resetting the database

`init.sql` only runs when the Docker volume is empty. To start from scratch:

```bash
docker compose down -v
docker compose up -d
```

## What I Learned

- Designing a clean **ETL** with separate extract, transform and load steps
- Making a pipeline **idempotent** (truncate and reload in one transaction)
- Running **PostgreSQL in Docker** and understanding how `docker-entrypoint-initdb.d` and `POSTGRES_DB` interact
- Managing secrets with **environment variables** instead of hard-coded credentials
- Writing **aggregation queries** in SQL (`DATE_TRUNC`, `COUNT(DISTINCT)`, `GROUP BY`)
- Building a data app with **Streamlit** (metrics, charts, caching, connections)
- Managing dependencies with **uv**

## Possible Improvements

- Star schema (fact table and dimensions) instead of a single flat table
- Sidebar filters (year, region, category) applied to every chart
- Unit tests for the `transform` step
- Structured logging instead of `print`
- Scheduling the pipeline (cron, Airflow or Prefect)
- Dockerizing the ETL and the dashboard in the same `compose.yml`

## Dataset

[Sample Superstore](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final): about 10,000 retail orders from 2014 to 2017.