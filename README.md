# ✈️ Flight Data Global Pipeline

Pipeline ETL para coleta, processamento e armazenamento de dados de voos em tempo real, utilizando Python, Apache Airflow e PostgreSQL.

---

## 📚 Visão Geral

- **Extração:** Coleta dados da API OpenSky Network e salva em JSON.
- **Transformação:** Normaliza, limpa e transforma os dados em CSV.
- **Carga:** Insere os dados processados em um banco PostgreSQL.
- **Orquestração:** Todo o fluxo é automatizado via Apache Airflow.

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

## ⚙️ Configuração do Ambiente

### 1. **Pré-requisitos**

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python 3.11+ (apenas para execução manual)

```
Crie um banco de dados local para acompanhar os dados caindo, insira as credênciais dele no .env e crie a tabela:

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

### 2. **Clone o Repositório**

```bash
git clone https://github.com/TiagoOliverDev/ETL_Pipeline_de_Dados_Climaticos
cd ETL_Pipeline_de_Dados_Climaticos
```

### 3. **Crie o Arquivo `.env`**

Baseie-se no modelo .env.example

### 4. **Suba o Ambiente com Docker Compose**

```bash
docker-compose up --build
```

- O Airflow estará disponível em: [http://localhost:8080](http://localhost:8080/)
- Usuário e senha definidos no `.env`

### 5. **Ative a DAG no Airflow**

1. Acesse a interface web do Airflow
2. Ative a DAG `flight_data_pipeline`
3. Você pode disparar manualmente ou aguardar a execução automática

---

## 🛠️ Execução Manual (fora do Airflow)

Se desejar rodar o pipeline manualmente:

```bash
python main.py
```

---

## 🧩 Principais Arquivos

- `dags/flight_data_dag.py`: DAG principal do Airflow
- `src/etl/extract_data.py`: Função de extração da API
- `src/etl/transform_data.py`: Funções de transformação
- `src/etl/load_data.py`: Função de carga no PostgreSQL
- `config/settings.py`: Parâmetros globais do pipeline
- `main.py`: Execução manual do pipeline

---

## 📝 Observações

- Os diretórios `data/raw`, `data/processed` e `logs` estão no `.gitignore`
- A tabela é criada automaticamente no banco se não existir
- O Airflow usa a conexão nomeada `postgres_etl_conn`

---

## 📚 Licença

Este projeto é open-source e está sob a licença MIT.

---

## 👩‍💻 Desenvolvido por

Tiago Oliveira – Analista desenvolvedor e Engenheiro de dados em formação

- 💼 [LinkedIn](https://www.linkedin.com/in/tiago-oliveira-49a2a6205/)
- 💻 [GitHub](https://github.com/TiagoOliverDev)

