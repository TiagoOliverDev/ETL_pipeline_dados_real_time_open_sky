import json
import time
import requests
import os
import sys
# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from kafka import KafkaProducer
from src.utils.logger import logger
from src.etl.extract_data import extract_data

KAFKA_TOPIC = "flight-data-raw"
KAFKA_BROKER = "localhost:9092"  # ou "kafka:9092" se rodando tudo via Docker

def get_flight_data():
    try:
        response = requests.get("https://opensky-network.org/api/states/all")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {e}")
        return None

def start_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    while True:
        data = get_flight_data()
        if data:
            producer.send(KAFKA_TOPIC, value=data)
            logger.info("🔁 Dados de voo enviados ao Kafka.")
        time.sleep(60)

if __name__ == "__main__":
    start_producer()
