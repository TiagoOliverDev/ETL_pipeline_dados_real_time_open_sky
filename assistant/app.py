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

def run_query(query: str, params=None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

# Campo de pergunta para IA
user_question = st.text_input("🧠 Digite sua pergunta sobre os voos:")
with st.expander("💡 Exemplos de perguntas que você pode fazer"):
    st.markdown("""
### ✈️ **Velocidade dos Voos**
- Quais são os 10 voos mais rápidos atualmente?
- Qual é a velocidade média dos voos em km/h?
- Quais voos estão voando abaixo de 200 km/h?
- Qual voo registrou a maior velocidade até agora?

### 🗻 **Altitude**
- Quais voos estão na maior altitude?
- Qual a altitude média dos voos neste momento?
- Qual voo voa na menor altitude?

### 🌍 **País de Origem**
- Quais os países com maior número de voos ativos?
- Quantos voos há saindo do Brasil agora?
- Qual país tem os voos mais rápidos?

### ⏰ **Tempo e Posição**
- Quais voos foram registrados nas últimas 2 horas?
- Qual o horário do último registro de voo do país selecionado?

### 🧠 **Perguntas Gerais**
- Há algum voo lento incomum acontecendo agora?
- Como está o tráfego aéreo em Natal neste momento?
- Quais voos estão próximos da minha localização?

    """)


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
    st.subheader("🗻 Top 10 Voos em Maior Altitude")
    df_altitude = run_query("""
        SELECT icao24, callsign, origin_country, geo_altitude
        FROM flight_data
        WHERE geo_altitude IS NOT NULL
        ORDER BY geo_altitude DESC
        LIMIT 10;
    """)
    st.dataframe(df_altitude)

    st.subheader("🐢 Top 10 Voos Mais Lentos")
    df_lentos = run_query("""
        SELECT icao24, callsign, origin_country, velocity
        FROM flight_data
        WHERE velocity IS NOT NULL AND velocity > 0
        ORDER BY velocity ASC
        LIMIT 10;
    """)
    st.dataframe(df_lentos)

# Filtro por país
st.markdown("---")
st.header("🌐 Filtrar por País de Origem")

df_paises_full = run_query("""
    SELECT DISTINCT origin_country FROM flight_data
    ORDER BY origin_country;
""")

paises = df_paises_full["origin_country"].dropna().tolist()
selected_country = st.selectbox("Selecione um país para ver os voos:", paises)

if selected_country:
    st.subheader(f"🛬 10 primeiros voos de {selected_country}")
    df_por_pais = run_query("""
        SELECT icao24, callsign, origin_country, velocity, latitude, longitude, time_position
        FROM flight_data
        WHERE origin_country = %s
        ORDER BY time_position DESC
        LIMIT 10;
    """, params=[selected_country])
    
    st.dataframe(df_por_pais)