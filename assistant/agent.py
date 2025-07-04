import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType

# Variáveis de ambiente
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "flights")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Instancia o banco
db = SQLDatabase.from_uri(DATABASE_URL)

# LLM da OpenAI (usando o novo pacote!)
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# Cria o agente baseado no banco
agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def ask_ai(question: str) -> str:
    try:
        # prompt = f"Responda apenas em português pt-br: {question}"
        prompt = f"Responda em português: {question}"
        return agent.run(prompt)
    except Exception as e:
        return f"❌ Erro ao processar a pergunta: {str(e)}"
