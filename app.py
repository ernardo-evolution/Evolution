import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ESTILIZAÇÃO VISUAL PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    h1, h2, h3 {
        color: #f0f6fc;
    }
    [data-testid="stSidebar"] {
        background-color: #11151c;
        border-right: 1px solid #21262d;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "evolution_gestao.db"

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

# --- 3. BASE DE DADOS E MIGRAÇÃO AUTOMÁTICA ---
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            username TEXT,
            email TEXT,
            senha TEXT,
            nivel TEXT,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto TEXT,
            quantidade INTEGER,
            valor_total REAL,
            data_venda TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            email TEXT,
            acao TEXT,
            detalhes TEXT,
            resultado TEXT,
            data_hora TEXT
        )
    """)
    
    conn.commit()

    def garantir_coluna(tabela, coluna, definicao):
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        if coluna not in colunas_existentes:
            try:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
                conn.commit()
            except Exception as e:
                print(f"Erro ao adicionar coluna {coluna} em {tabela}: {e}")

    garantir_coluna("clientes", "email", "TEXT")
    garantir_coluna("clientes", "telefone", "TEXT")
    garantir_coluna("clientes", "cidade", "TEXT")
    garantir_coluna("clientes", "data_cadastro", "TEXT")

    garantir_coluna("produtos", "preco", "REAL DEFAULT 0.0")
    garantir_coluna("produtos", "stock", "INTEGER DEFAULT 0")

    conn.close()
except Exception as e:
    st.error(f"Erro na BD: {e}")

def registar_log(usuario, email, acao, detalhes, resultado):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            "INSERT INTO historico (usuario, email, acao, detalhes, resultado, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
            (usuario or "Anónimo", email or "N/D", acao, detalhes, resultado, data_hora)
        )
        conn.commit()
        conn.close()
    except Exception as ex:
        print(f"Erro ao gravar log: {ex}")

# --- 4. GESTÃO DE SESSÃO E PERSISTÊNCIA ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = ""
if "email_atual" not in st.session_state:
    st.session_state["email_atual"] = ""
if "nivel_acesso" not in st.session_state:
    st.session_state["nivel_acesso"] = ""
if "email_input" not in st.session_state:
    st.session_state["email_input"] = ""

# Persistência via URL (Lembrar de mim)
try:
    query_params = st.query_params
    email_persisted = query_params.get("email", None)
    if not st.session_state["autenticado"] and email_persisted:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, nivel, email FROM usuarios WHERE email = ?", (email_persisted,))
        user_persisted = cursor.fetchone()
        conn.close()
        if user_persisted:
            st.session_state["autenticado"] = True
            st.session_state["usuario_atual"] = user_persisted[0]
            st.session_state["nivel_acesso"] = user_persisted[1]
            st.session_state["email_atual"] = user_persisted[2]
except Exception as ex:
    print(f"Erro na persistência: {ex}")

# --- 5. BARRA LATERAL E NAVEGAÇÃO ---
menu = "Dashboard"
with st.sidebar:
    st.markdown("### 🚀 Evolution Gestão")
    st.markdown("---")
    if st.session_state["autenticado"]:
        st.markdown(f"👤 **{st.session_state['usuario_atual']}**\n📧 `{st.session_state['email_atual']}`\n🔑 Nível: `{st.session_state['nivel_acesso']}`")
        st.markdown("---")
        
        opcoes_menu = ["📊 Dashboard", "👥 Clientes", "📦 Produtos & Stock", "🛒 Vendas", "📋 Relatórios"]
        if st.session_state["nivel_acesso"] == "Administrador":
            opcoes_menu.append("🛡️ Logs e Auditoria")
            
        menu = st.selectbox("Menu Principal", opcoes_menu)
        
        st.markdown("---")
        if st.button("Terminar Sessão", use_container_width=True):
            registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Logout", "Encerramento de sessão", "Sucesso")
            if "email" in st.query_params:
                del st.query_params["email"]
            st.session_state["autenticado"] = False
            st.session_state["usuario_atual"] = ""
            st.session_state["email_atual"] = ""
            st.session_state["nivel_acesso"] = ""
            st.rerun()
    else:
        st.warning("⚠️ Efetue login para aceder.")

# --- 6. INTERFACE DE LOGIN / REGISTO ---
if not st.session_state["autenticado"]:
    st.title("🚀 A Evolution Gestão Online")
    
    tab1, tab2 = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])
    
    with tab1:
        st.markdown("### Acesso Restrito ao Sistema")
        with st.form("form_login"):
            email = st.text_input("E-mail corporativo", value=st.session_state["email_input"]).strip().lower()
            senha = st.text_input("Palavra-passe", type="password")
            lembrar = st.checkbox("Lembrar de mim neste dispositivo")
            entrar
