import requests
import os
import json
from config.settings import FILES_FOLDER_RAW
from src.utils.logger import logger
from pathlib import Path

def extract_data(output_path: Path, execution_dt: str = None):
    """
    Extrai dados de voos em tempo real da OpenSky Network e salva como JSON.

    :param output_path: Caminho para salvar o arquivo.
    :param execution_dt: Timestamp da execução (usado no nome do arquivo).
    """

    url = 'https://opensky-network.org/api/states/all'
    
    headers = {
        "User-Agent": "api-voo-pipeline/1.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url=url, timeout=10, headers=headers)
        response.raise_for_status() 
        data = response.json()
    except Exception as e:
        logger.error(f'Erro ao fazer requisição para OpenSky API: {e}')
        raise

    os.makedirs(FILES_FOLDER_RAW, exist_ok=True)

    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        logger.info(f'✅ Dados salvos com sucesso em: {output_path}')
    except Exception as e:
        logger.error(f'Erro ao salvar arquivo: {e}')
        raise
