from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'amilton',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'daily_scraper_job',
    default_args=default_args,
    description='Executa o script de scraping diariamente',
    schedule_interval='0 7 * * *',  # 07:00 todo dia
    catchup=False,
    tags=['scraping'],
) as dag:

    run_scraper = BashOperator(
        task_id='run_scraper_script',
        bash_command='PYTHONPATH=/opt/airflow/scripts python3 /opt/airflow/scripts/scraper.py',
    )

    run_ingest = BashOperator(
        task_id='run_ingest_script',
        bash_command='python3 /opt/airflow/scripts/ingest_data.py',
    )

    run_scraper >> run_ingest