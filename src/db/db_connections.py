import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.logger import logger
from dotenv import load_dotenv

_ = load_dotenv()

def get_engine_from_env():
    user = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    database = os.getenv('DATABASE')

    if all([user, password, host, port, database]):
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return create_engine(url)
    return None

def get_engine_from_airflow(conn_id='local_postgres_conn'):
    try:
        from airflow.hooks.base import BaseHook
    except ImportError as e:
        raise ImportError("Airflow não está instalado neste ambiente. Use .env para conexão local.") from e

    connection = BaseHook.get_connection(conn_id)

    user = connection.login
    password = connection.password
    host = connection.host
    port = connection.port
    schema = connection.schema

    url = f"postgresql://{user}:{password}@{host}:{port}/{schema}"
    return create_engine(url)

def is_running_in_airflow():
    # Verifica se está dentro do contexto do Airflow
    return 'AIRFLOW_CTX_DAG_ID' in os.environ

def connect_db_sqlalchemy():
    try:
        if is_running_in_airflow():
            logger.info("🌀 Executando via Airflow. Usando Connection UI...")
            return get_engine_from_airflow()
        else:
            logger.info("🧪 Executando via main.py. Usando variáveis .env...")
            engine = get_engine_from_env()
            if engine is None:
                raise ValueError("Variáveis de ambiente para conexão estão incompletas.")
            return engine
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise e

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
