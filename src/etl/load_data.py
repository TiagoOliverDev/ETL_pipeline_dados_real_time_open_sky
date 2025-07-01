import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_connections import connect_db_sqlalchemy  
from src.utils.logger import logger


def load_data(df: pd.DataFrame):
    """
    Recebe um DataFrame de dados de voos e insere na tabela flight_data do PostgreSQL.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("O objeto recebido não é um DataFrame válido.")
    
    try:
        engine = connect_db_sqlalchemy()

        df.to_sql(
            name='flight_data',         
            con=engine,
            if_exists='append',         # Adiciona (não sobrescreve)
            index=False
        )

        logger.info("✅ Dados inseridos na tabela flight_data com sucesso!")
    
    except SQLAlchemyError as e:
        logger.error(f"❌ Erro ao inserir dados no banco: {e}")
        raise
