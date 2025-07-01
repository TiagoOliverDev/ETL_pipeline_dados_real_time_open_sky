from src.etl.extract_data import extract_data
from src.etl.transform_data import transform_data
from src.etl.load_data import load_data
from datetime import datetime
from pathlib import Path
from config.settings import FILES_FOLDER_RAW, PROCESSED_DATA_DIR, NATAL_TZ
from src.utils.logger import logger
import json


def main():
    """
    Executa o pipeline ETL completo para coleta, transformação e carregamento
    dos dados de tráfego aéreo da API OpenSky.
    """
    DATETIME = datetime.now(NATAL_TZ)
    TIMESTAMP = DATETIME.strftime('%Y-%m-%d_%H-%M-%S')
    output_path = Path(FILES_FOLDER_RAW) / f"flight_data_{TIMESTAMP}.json"

    try:
        logger.info("=" * 50)
        logger.info("Iniciando pipeline ETL - OpenSky Flight Data ✈️")
        logger.info("=" * 50)

        logger.info("\n🔎 [1/3] Extraindo dados da API OpenSky...")
        extract_data(output_path=output_path, execution_dt=TIMESTAMP)
        logger.info(f"✅ Arquivo extraído: {output_path}\n")

        logger.info("🛠️ [2/3] Transformando dados do JSON para DataFrame...")
        # Carrega JSON do arquivo salvo
        with open(output_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
        
        data_dict = json.loads(raw_data)

        processed_df = transform_data(
            data=data_dict,
            processed_data_dir=Path(PROCESSED_DATA_DIR),
            timestamp=TIMESTAMP
        )
        logger.info("✅ Transformação concluída\n")

        logger.info("🚚 [3/3] Enviando dados para o banco de dados...")
        load_data(df=processed_df)
        logger.info("✅ Dados inseridos no banco com sucesso!\n")

        logger.info("=" * 50)
        logger.info("🏁 Pipeline finalizado com sucesso!")
        logger.info("=" * 50)

    except Exception as e:
        logger.warning("=" * 50)
        logger.error(f"❌ Ocorreu um erro no pipeline: {e}")
        logger.warning("=" * 50)


if __name__ == "__main__":
    main()
