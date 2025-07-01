import pandas as pd
from datetime import datetime
from pathlib import Path
from config.settings import NATAL_TZ
from src.utils.logger import logger


def transform_data(data: dict, processed_data_dir: Path, timestamp: str):
    """
    Transforma os dados brutos da API OpenSky e salva em formato CSV com colunas padronizadas.

    :param data: Dicionário JSON carregado da API (já convertido via json.load ou json.loads).
    :param processed_data_dir: Diretório para salvar os dados processados.
    :param timestamp: Timestamp (str) da execução, usado no nome do arquivo.
    :return: DataFrame transformado.
    """
    columns = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact",
        "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
        "heading", "vertical_rate", "sensors", "geo_altitude", "squawk",
        "spi", "position_source"
    ]

    try:
        df = pd.DataFrame(data.get("states", []), columns=columns)

        # Remove espaços em branco no callsign e converte datas
        df["callsign"] = df["callsign"].str.strip()

        # Converte timestamps (Unix) para datetime
        df["time_position"] = pd.to_datetime(df["time_position"], unit='s', utc=True)
        df["last_contact"] = pd.to_datetime(df["last_contact"], unit='s', utc=True)

        # Adiciona horário local de execução
        df["record_timestamp"] = pd.to_datetime(datetime.now(NATAL_TZ)).floor('s')

        # Ordena colunas para facilitar leitura
        df = df[["icao24", "callsign", "origin_country", "latitude", "longitude", "velocity",
                 "heading", "baro_altitude", "geo_altitude", "on_ground", "time_position", 
                 "last_contact", "record_timestamp"]]

        # Cria diretório (se necessário) e salva CSV
        output_filename = f"processed_flight_data_{timestamp}.csv"
        output_path = processed_data_dir / output_filename
        processed_data_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        logger.info(f"✅ Dados transformados salvos em {output_path}")
        return df

    except Exception as e:
        logger.error(f"Erro ao transformar dados: {e}")
        raise
