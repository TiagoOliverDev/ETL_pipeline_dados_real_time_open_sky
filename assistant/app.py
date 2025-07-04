import streamlit as st
import os
import psycopg2
import pandas as pd
from agent import ask_ai

# Configuração da página
st.set_page_config(page_title="Flight Data Assistant", layout="wide")
st.title("✈️ Assistente Inteligente de Voos")

# Funções de banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "flights")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def run_query(query: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)

# Campo de pergunta para IA
user_question = st.text_input("🧠 Digite sua pergunta sobre os voos:")

if user_question:
    with st.spinner("Consultando IA..."):
        resposta = ask_ai(user_question)
        st.success(resposta)

# Visualização de dados do banco
st.markdown("---")
st.header("📊 Painel de Dados de Voos")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔝 Top 10 Voos Mais Rápidos")
    df_rapidos = run_query("""
        SELECT icao24, callsign, origin_country, velocity
        FROM flight_data
        ORDER BY velocity DESC
        LIMIT 10;
    """)
    st.dataframe(df_rapidos)

    st.subheader("🚀 Top 10 Velocidades em km/h")
    df_kmh = run_query("""
        SELECT 
            icao24, 
            callsign, 
            origin_country, 
            ROUND((velocity * 3.6)::numeric, 2) AS velocidade_kmh
        FROM flight_data
        ORDER BY velocidade_kmh DESC
        LIMIT 10;
    """)
    st.dataframe(df_kmh)

with col2:
    st.subheader("🌍 Ranking de Voos por País")
    df_paises = run_query("""
        SELECT origin_country, COUNT(*) AS total_voos
        FROM flight_data
        GROUP BY origin_country
        ORDER BY total_voos DESC
        LIMIT 10;
    """)
    st.dataframe(df_paises)

    st.subheader("🗻 Top 10 Voos em Maior Altitude")
    df_altitude = run_query("""
        SELECT icao24, callsign, origin_country, geo_altitude
        FROM flight_data
        WHERE geo_altitude IS NOT NULL
        ORDER BY geo_altitude DESC
        LIMIT 10;
    """)
    st.dataframe(df_altitude)
