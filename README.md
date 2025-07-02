# ✈️ Flight Data Global Pipeline

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Airflow DAG](https://img.shields.io/badge/Airflow-DAG-blue)](http://localhost:8080)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-✔️-blue)](https://www.postgresql.org/)
[![Kafka + Spark Streaming](https://img.shields.io/badge/Streaming-Kafka%20%2B%20Spark-orange)](https://spark.apache.org/structured-streaming/)

Pipeline ETL e de **streaming** para coleta, processamento e armazenamento de dados de voos em tempo real, utilizando **Python**, **Apache Airflow**, **Apache Kafka**, **Apache Spark Structured Streaming** e **PostgreSQL**.

---

## 📚 Visão Geral

- **Extração (batch e streaming):**
  - Batch: coleta periódica via DAG no Airflow a partir da API OpenSky Network.
  - Streaming: dados produzidos continuamente em tópicos Kafka.
- **Transformação:** dados normalizados, limpos e enriquecidos via pandas (batch) ou Spark Structured Streaming (tempo real).
- **Carga:** os dados são inseridos ou atualizados no banco PostgreSQL.
- **Orquestração:** Airflow gerencia tarefas em lote; Kafka + Spark processam o fluxo contínuo.

---

## 🗂️ Estrutura do Projeto

```bash
ETL_pipeline_dados_real_time_open_sky/
├── config/
│   └── settings.py
├── dags/
│   └── flight_data_dag.py
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── notebooks/
├── plugins/
├── src/
│   ├── db/
│   │   └── db_connections.py
│   ├── etl/
│   │   ├── extract_data.py
│   │   ├── json_loader.py
│   │   ├── load_data.py
│   │   └── transform_data.py
│   ├── streaming/
│   │   └── kafka_consumer.py
│   │   └── structured_streaming.py
│   ├── utils/
│   │   └── logger.py
├── tests/
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── main.py
```

---

## ⚙️ Arquitetura do Processamento de Streaming

```bash
+------------------+        +------------------+        +--------------------------+
|     Producer     | -----> |   Kafka Topic    | -----> | Spark Structured Stream  |
| (OpenSky + ETL)  | JSON   | flight-data-raw  |        |  Transform + PostgreSQL  |
+------------------+        +------------------+        +--------------------------+
                                                    └─>  UPSERT (merge/update)
```

---

## ⚙️ Configuração do Ambiente

### 1. **Pré-requisitos**

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python 3.11+ (para execuções locais e testes)

Crie um banco PostgreSQL e insira as credenciais no `.env`. Use o seguinte esquema:

```sql
CREATE TABLE IF NOT EXISTS flight_data (
    icao24 VARCHAR(10) NOT NULL,
    callsign VARCHAR(10),
    origin_country VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    baro_altitude DOUBLE PRECISION,
    geo_altitude DOUBLE PRECISION,
    on_ground BOOLEAN,
    time_position TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_contact TIMESTAMP WITHOUT TIME ZONE,
    record_timestamp TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (icao24, time_position)
);
```

---

### 2. **Clone o Repositório**

```bash
git clone https://github.com/TiagoOliverDev/ETL_Pipeline_de_Dados_Climaticos
cd ETL_Pipeline_de_Dados_Climaticos
```

---

### 3. **Crie o Arquivo `.env`**

Baseie-se no modelo `.env.example`.

---

### 4. **Suba o Ambiente com Docker Compose**

```bash
docker-compose up --build
```

- Airflow: [http://localhost:8080](http://localhost:8080)
- Kafka: padrão porta 9092
- PostgreSQL: conforme definido no `.env`

---

### 5. **Ative a DAG no Airflow**

1. Acesse a interface web do Airflow
2. Ative a DAG `flight_data_pipeline`
3. Configure a conexão `postgres_etl_conn` com seu banco
4. Dispare manualmente ou aguarde execução automática

---

## 🛠️ Execução Manual (fora do Airflow)

```bash
python main.py
```

Para execução do consumidor Spark Streaming (caso não esteja orquestrado via DAG):

```bash
spark-submit src/streaming/spark_streaming_consumer.py
```

---

## 🧩 Principais Arquivos

| Caminho | Descrição |
|--------|-----------|
| `dags/flight_data_dag.py` | DAG principal (Airflow) |
| `src/etl/extract_data.py` | Coleta dados da OpenSky API |
| `src/etl/transform_data.py` | Limpa e normaliza os dados |
| `src/etl/load_data.py` | Carga no PostgreSQL |
| `src/streaming/kafka_producer.py` |Envia dados em forma de mensagem na fila a cada 60 segundos |
| `src/streaming/structured_streaming.py` | Consome dados do Kafka e grava no banco |
| `config/settings.py` | Configurações globais |
| `main.py` | Execução local (batch) |

---

## 📝 Observações

- Os diretórios `data/raw`, `data/processed` e `logs` estão no `.gitignore`
- A tabela `flight_data` é criada automaticamente se não existir
- Airflow usa a conexão `postgres_etl_conn`
- Kafka pode ser executado via Docker ou serviço externo

---

## 📚 Licença

Este projeto é open-source e está sob a licença [MIT](LICENSE).

---

## 👨‍💻 Desenvolvido por

**Tiago Oliveira**  
Analista desenvolvedor e Engenheiro de dados em formação

- 💼 [LinkedIn](https://www.linkedin.com/in/tiago-oliveira-49a2a6205/)
- 💻 [GitHub](https://github.com/TiagoOliverDev)