import streamlit as st
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ESTILIZAÇÃO VISUAL ---
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

# --- 3. BASE DE DADOS ---
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
    conn.commit()
    conn.close()
except Exception as e:
    st.error(f"Erro na BD: {e}")

# --- 4. GESTÃO DE SESSÃO SEGURA ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = ""
if "nivel_acesso" not in st.session_state:
    st.session_state["nivel_acesso"] = ""

# Se estiver marcado como autenticado mas o nome estiver vazio, força reset
if st.session_state["autenticado"] and not st.session_state["usuario_atual"]:
    st.session_state["autenticado"] = False

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.markdown("### Evolution Corp Brasil")
    st.markdown("---")
    if st.session_state["autenticado"]:
        st.markdown(f"👤 **{st.session_state['usuario_atual']}**\n🔑 Nível: `{st.session_state['nivel_acesso']}`")
        st.markdown("---")
        if st.button("Terminar Sessão", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario_atual"] = ""
            st.session_state["nivel_acesso"] = ""
            st.rerun()
    else:
        st.warning("⚠️ Efetue login para aceder.")

# --- 6. INTERFACE PRINCIPAL ---
if not st.session_state["autenticado"]:
    st.title("🚀 A Evolution Gestão Online")
    
    tab1, tab2 = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])
    
    with tab1:
        st.markdown("### Acesso Direto ao Sistema")
        with st.form("form_login"):
            email = st.text_input("E-mail corporativo").strip().lower()
            senha = st.text_input("Palavra-passe", type="password")
            entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if entrar:
                if email and senha:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, nivel, senha FROM usuarios WHERE email = ?", (email,))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user and user[2] == gerar_hash_senha(senha):
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_atual"] = user[0]
                        st.session_state["nivel_acesso"] = user[1]
                        st.success("Sessão iniciada com sucesso!")
                        st.rerun()
                    else:
                        st.error("E-mail ou palavra-passe incorretos.")
                else:
                    st.warning("Preencha todos os campos.")
                    
    with tab2:
        st.markdown("### Criar Conta Rápida")
        with st.form("form_registo"):
            r_nome = st.text_input("Nome Completo")
            r_user = st.text_input("Username")
            r_email = st.text_input("E-mail Corporativo")
            r_senha = st.text_input("Palavra-passe (mín. 6 caracteres)", type="password")
            r_nivel = st.selectbox("Nível de Acesso", ["Administrador", "Gerente", "Funcionário"])
            registar = st.form_submit_button("Criar Conta", use_container_width=True)
            
            if registar:
                if r_nome and r_email and r_senha:
                    if len(r_senha) < 6:
                        st.error("A palavra-passe deve ter pelo menos 6 caracteres.")
                    else:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (r_email.lower(),))
                        if cursor.fetchone():
                            conn.close()
                            st.error("Este e-mail já está registado.")
                        else:
                            cursor.execute(
                                "INSERT INTO usuarios (nome, username, email, senha, nivel, ativo) VALUES (?, ?, ?, ?, ?, 1)",
                                (r_nome, r_user, r_email.lower(), gerar_hash_senha(r_senha), r_nivel)
                            )
                            conn.commit()
                            conn.close()
                            st.success("Conta criada com sucesso! Vá à aba 'Iniciar Sessão' para entrar.")
                else:
                    st.warning("Preencha os campos obrigatórios.")
else:
    st.header("📊 Painel Principal — Evolution Gestão Online")
    st.markdown(f"Bem-vindo(a) de volta, **{st.session_state['usuario_atual']}**!")
    st.info("O sistema está totalmente operacional e pronto para gerir as suas operações.")
