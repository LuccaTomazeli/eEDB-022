from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def teste_airflow():
    print("========================================")
    print("Atividade 5 - Airflow funcionando!")
    print("========================================")


with DAG(
    dag_id="atividade_05_teste",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["atividade_05", "teste"],
) as dag:

    teste = PythonOperator(
        task_id="teste_airflow",
        python_callable=teste_airflow,
    )