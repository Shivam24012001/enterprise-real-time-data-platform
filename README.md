# LendPulse: an end-to-end lending data platform

> Work in progress. Current release: **v0.1 Foundation**. Synthetic data only; no real customer data is ever used.

## Goal

LendPulse is a personal portfolio project: the data platform for a simulated Indian NBFC (Loan Against Property and personal loans). When finished, it will:

- simulate a lender's loan system (applications, EMI schedules, repayments, NACH bounces);
- land that data in a raw zone, transform it with **dbt** (DuckDB locally, Snowflake in the cloud) into risk marts such as DPD buckets, SMA/NPA classification, roll rates and vintage curves;
- orchestrate everything with **Airflow**, reconcile every run against the source, and mask PII by role.

It is built in public, one story at a time: every story is a GitHub issue on the project board (see the **Projects** tab), delivered through its own branch and pull request.

## What runs today

| Part | What it does | Code |
| --- | --- | --- |
| Local stack | Postgres 17 and MinIO (S3-compatible storage) in Docker; MinIO pinned by image digest | `docker-compose.yml` |
| Configuration | Non-secret settings in YAML; credentials only from `.env` via pydantic-settings | `configs/`, `ingestion/config_loader.py`, `ingestion/settings.py` |
| API ingestion | Config-driven REST ingestion (sample: JSONPlaceholder `/posts`) into MinIO under date-partitioned keys | `ingestion/`, `storage/` |
| Retries | Exponential backoff with jitter for timeouts, connection errors, 429 and 5xx; other 4xx fail at once | `ingestion/retry.py` |
| Spark reading | JSON read in PERMISSIVE mode; malformed records are quarantined with their raw text, source file and reason | `processing/reader.py`, `processing/quarantine.py` |
| Data quality | Required columns, null counts and duplicates; a failed check raises `DataQualityError` naming the column and count | `processing/quality/` |
| Tests | pytest suite (no network or cloud needed) and ruff linting | `tests/` |

**Not built yet:** the lending simulator, dbt models, Airflow, Snowflake, CDC, streaming and CI. See the roadmap.

## How to run

Prerequisites: Docker Desktop, Python 3.12, [Poetry](https://python-poetry.org/) 2.x, and Java 17 or 21 (needed by Spark).

```bash
git clone https://github.com/Shivam24012001/enterprise-real-time-data-platform.git
cd enterprise-real-time-data-platform

cp .env.example .env        # then replace the change-me passwords
docker compose up -d        # Postgres on 5432, MinIO on 9000 (console on 9001)
poetry install
```

Check that everything works:

```bash
poetry run pytest -q                        # full test suite
poetry run ruff check src tests scripts     # linting
poetry run python scripts/test_spark.py     # Spark starts locally
```

Run the sample ingestion:

1. First run only: open the MinIO console at http://localhost:9001, log in with `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from `.env`, and create a bucket named `enterprise-platform`.
2. Run `poetry run python scripts/test_upload.py`. It downloads the enabled API from `configs/apis/apis.yaml` and uploads it to MinIO.

See retries in action against a real HTTP 503 (needs internet):

```bash
poetry run python scripts/demo_retry.py
```

## Project structure

```
configs/                 YAML settings (no secrets) and API definitions
scripts/                 manual demo scripts
src/enterprise_platform/
  ingestion/             config loading, secrets, HTTP client, retries, ingestion service
  processing/            Spark session, JSON reader, quarantine, data quality checks, schemas
  storage/               MinIO client, uploader, object key builder
tests/                   pytest suite
```

## Roadmap

| Release | What ships | Target |
| --- | --- | --- |
| v0.1 Foundation | Clean, tested base: secrets, retries, quarantine, data quality, README | Dec 2026 |
| v0.2 dbt on DuckDB | Lending simulator, raw extract, dbt staging, DPD and NPA marts, first dashboard | Feb 2027 |
| v0.3 Orchestrated | CI, chaos injection, Airflow running dbt, backfills, reconciliation | Apr 2027 |
| v0.4 Risk analytics | SCD2 snapshots, incremental models, risk marts, public dbt docs | May 2027 |
| v1.0 Portfolio-ready | The same dbt project on Snowflake, PII masking, demo video | Jun 2027 |

After v1.0: CDC with Debezium and Kafka, a Databricks lakehouse, real-time early-warning signals, and an AI agent that answers portfolio questions. Targets are reviewed every two-week sprint.
