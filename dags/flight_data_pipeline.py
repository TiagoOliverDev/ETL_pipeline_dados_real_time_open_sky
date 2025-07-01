import sys
import json
import pendulum
import pandas as pd
from pathlib import Path
from datetime import datetime
from datetime import datetime

DAG_FOLDER = Path(__file__).parent
PROJECT_ROOT = DAG_FOLDER.parent
sys.path.append(str(PROJECT_ROOT))

from airflow.decorators import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from src.etl.extract_data import extract_data
from src.etl.transform_data import transform_data
from src.etl.load_data import load_data
from config.settings import FILES_FOLDER_RAW, PROCESSED_DATA_DIR, NATAL_TZ


@dag(
    dag_id='flight_data_pipeline',
    start_date=pendulum.datetime(2024, 1, 1, tz="America/Recife"),
    schedule_interval='@hourly', 
    catchup=False,
    tags=["etl", "aviation", "opensky"],
    doc_md="""
    ### ✈️ Pipeline ETL - Dados de Voos (OpenSky)
    Coleta dados de tráfego aéreo global, transforma e insere no PostgreSQL.
    """
)
def dag_flight_data_pipeline():
    
    DATETIME = datetime.now(NATAL_TZ)
    TIMESTAMP = DATETIME.strftime('%Y-%m-%d_%H-%M-%S')

    @task()
    def extract():
        execution_dt = datetime.now(NATAL_TZ)
        timestamp = execution_dt.strftime('%Y-%m-%d_%H-%M-%S')
        output_path = FILES_FOLDER_RAW / f"flight_data_{timestamp}.json"
        extract_data(output_path=output_path, execution_dt=timestamp)
        return str(output_path)

    @task()
    def transform(output_path: str):
        with open(output_path, "r", encoding="utf-8") as f:
            data_dict = json.load(f)

        processed_df = transform_data(
            data=data_dict,
            processed_data_dir=PROCESSED_DATA_DIR,
            timestamp=TIMESTAMP
        )
        return processed_df.to_json(orient="records", date_format='iso')

    @task()
    def load(processed_json: str):
        df = pd.read_json(processed_json)
        load_data(df)

    ensure_table_exists = SQLExecuteQueryOperator(
        task_id="ensure_table_exists",
        conn_id="local_postgres_conn",
        sql="""
            CREATE TABLE IF NOT EXISTS flight_data (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(10),
                callsign VARCHAR(10),
                origin_country VARCHAR(100),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                velocity DOUBLE PRECISION,
                heading DOUBLE PRECISION,
                baro_altitude DOUBLE PRECISION,
                geo_altitude DOUBLE PRECISION,
                on_ground BOOLEAN,
                time_position TIMESTAMPTZ,
                last_contact TIMESTAMPTZ,
                record_timestamp TIMESTAMP
            );
        """
    )

    # Orquestração das tasks
    extracted = extract()
    transformed = transform(extracted)
    transformed >> ensure_table_exists
    ensure_table_exists >> load(transformed)

dag_flight_data_pipeline()
