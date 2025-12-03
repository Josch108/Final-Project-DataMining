"""
Airflow DAG for the Apriori market-basket analysis pipeline.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Ensure project scripts are importable when running inside Airflow
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.load_data import clean_transactions  # noqa: E402
from scripts.apriori import AprioriConfig, run_apriori_pipeline  # noqa: E402
from scripts.generate_report import generate_report  # noqa: E402


def _run_apriori():
    run_apriori_pipeline(config=AprioriConfig())


def _generate_report():
    generate_report()


default_args = {
    "owner": "data_engineer",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="apriori_pipeline",
    description="Mini data mining pipeline using Apriori",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["apriori", "market-basket"],
) as dag:
    load_clean_task = PythonOperator(
        task_id="extract_and_clean",
        python_callable=clean_transactions,
    )

    apriori_task = PythonOperator(
        task_id="run_apriori",
        python_callable=_run_apriori,
    )

    report_task = PythonOperator(
        task_id="generate_report",
        python_callable=_generate_report,
    )

    load_clean_task >> apriori_task >> report_task
