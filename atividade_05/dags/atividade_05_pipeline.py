from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="pipeline_atividade_05",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=[
        "atividade_05",
        "data_engineering",
        "dbt",
        "great_expectations",
    ],
) as dag:

    ingest_raw = BashOperator(
        task_id="ingest_raw",
        bash_command=(
            "cd /opt/atividade_05/scripts && "
            "python ingest_raw.py"
        ),
    )

    depara_bcb = BashOperator(
        task_id="depara_bcb",
        bash_command=(
            "cd /opt/atividade_05/scripts && "
            "python depara_bcb.py"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/atividade_05/dbt && "
            "dbt run --profiles-dir ."
        ),
    )

    quality_check = BashOperator(
        task_id="quality_check",
        bash_command=(
            "cd /opt/atividade_05/scripts && "
            "python quality_check.py"
        ),
    )

    export_parquet = BashOperator(
        task_id="export_parquet",
        bash_command=(
            "cd /opt/atividade_05/scripts && "
            "python export_parquet.py"
        ),
    )

    ingest_raw >> depara_bcb >> dbt_run >> quality_check >> export_parquet