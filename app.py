from datetime import datetime, timedelta
import hashlib
import sqlite3
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ESTILIZAÇÃO VISUAL (TEMA ESCURO GRAFITE) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3 {
        color: #f0f6fc;
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    [data-testid="stSidebar"] {
        background-color: #11151c;
        border-right: 1px solid #21262d;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "evolution_gestao.db"

# --- 3. MAPEAMENTO DE PAÍSES E MOEDAS ---
PAISES_MOEDAS = {
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português"},
    "Estados Unidos": {"moeda": "USD", "simbolo": "US$", "idioma": "English"},
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español"},
    "Reino Unido": {"moeda": "GBP", "simbolo": "£", "idioma": "English"},
}

# --- 4. FUNÇÕES DE SEGURANÇA E HASH ---
def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

# --- 5. INICIALIZAÇÃO DA BASE DE DADOS ---
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            pais TEXT,
            pais_registro TEXT,
            moeda TEXT,
            simbolo TEXT,
            idioma TEXT,
            fuso TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            username TEXT,
            email TEXT,
            senha TEXT,
            nivel TEXT,
            ativo INTEGER DEFAULT 1,
            session_token TEXT,
            token_expiry TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            username TEXT,
            email TEXT,
            acao TEXT,
            detalhes TEXT,
            resultado TEXT,
            servico TEXT,
            codigo_erro TEXT,
            rastreamento_id TEXT,
            data_hora TEXT
        )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM empresa")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo, idioma, fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Evolution Corp Brasil", "Brasil", "Brasil", "BRL", "R$", "Português", "UTC-3"),
        )
        conn.commit()

    conn.close()
except Exception as db_err:
    st.error(f"Erro crítico ao inicializar a base de dados: {db_err}")
    st.stop()

# --- 6. FUNÇÕES AUXILIARES ---
def carregar_empresa():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, pais, pais_registro, moeda, simbolo, idioma, fuso FROM empresa LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            pais_l = row[1] or "Brasil"
            info_pais = PAISES_MOEDAS.get(pais_l, PAISES_MOEDAS["Brasil"])
            return {
                "nome": row[0] or "Evolution Corp Brasil",
                "pais": pais_l,
                "pais_registro": row[2] or "Brasil",
                "moeda": row[3] or info_pais["moeda"],
                "simbolo": row[4] or info_pais["simbolo"],
                "idioma": row[5] or info_pais["idioma"],
                "fuso": row[6] or "UTC-3",
            }
    except Exception as e:
