from datetime import datetime, timedelta
import hashlib
import random
import secrets
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "evolution_gestao.db"

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def mascarar_email(email):
    if "@" not in email:
        return email
    partes = email.split("@")
    return f"{partes[0][:2]}****@{partes[1]}"

# Inicialização da Base de Dados
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
            ativo INTEGER DEFAULT 0,
            codigo_verificacao TEXT,
            codigo_expiracao TEXT,
            tentativas_codigo INTEGER DEFAULT 0,
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
    conn.close()
except Exception as e:
    st.error(f"Erro na BD: {e}")

def disparar_emailjs(destinatario, nome_usuario, codigo, rastreamento_id):
    try:
        ej_conf = st.secrets.get("emailjs", {})
    except:
        ej_conf = {}

    service_id = ej_conf.get("service_id", "service_15qkad9")
    template_id = ej_conf.get("template_id", "0f4y8it")
    public_key = ej_conf.get("public_key", "PCUYqPfeqGqMvHbaD")

    html_code = f"""
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
        <script type="text/javascript">
           (function(){{ emailjs.init("{public_key}"); }})();
           var templateParams = {{
              to_email: "{destinatario}",
              to_name: "{nome_usuario}",
              codigo: "{codigo}",
              rastreamento: "{rastreamento_id}"
           }};
           emailjs.send("{service_id}", "{template_id}", templateParams);
        </script>
    """
    components.html(html_code, height=0, width=0)
    return True, "Enviado"

# Gestão de Sessão
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = ""
if "nivel_acesso" not in st.session_state:
    st.session_state["nivel_acesso"] = ""
if "aguardando_verificacao" not in st.session_state:
    st.session_state["aguardando_verificacao"] = None
if "modo_recuperacao" not in st.session_state:
    st.session_state["modo_recuperacao"] = False

if not st.session_state["autenticado"]:
    st.title("🚀 A Evolution Gestão Online")

    if st.session_state["modo_recuperacao"]:
        st.markdown("### 🔑 Obter Código Direto por E-mail")
        with st.form("form_rec"):
            email_rec = st.text_input("E-mail corporativo").strip().lower()
            c1, c2 = st.columns(2)
            btn_rec = c1.form_submit_button("Enviar Código", use_container_width=True)
            btn_voltar = c2.form_submit_button("Voltar ao Login", use_container_width=True)

            if btn_rec:
                if "@" in email_rec:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email_rec,))
                    u = cursor.fetchone()
                    if u:
                        novo_cod = f"{random.randint(0, 999999):06d}"
                        exp = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("UPDATE usuarios SET codigo_verificacao = ?, codigo_expiracao = ? WHERE id = ?", (novo_cod, exp, u[0]))
                        conn.commit()
                        conn.close()
                        disparar_emailjs(email_rec, u[1], novo_cod, "rec")
                        st.session_state["aguardando_verificacao"] = email_rec
                        st.session_state["modo_recuperacao"] = False
                        st.success("Código enviado para o seu e-mail!")
                        st.rerun()
                    else:
                        conn.close()
                        st.error("E-mail não encontrado.")
            if btn_voltar:
                st.session_state["modo_recuperacao"] = False
                st.rerun()
    else:
        tab1, tab2 = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])
        
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail").strip().lower()
                senha = st.text_input("Palavra-passe", type="password")
                entrar = st.form_submit_button("Entrar")
                
                if entrar:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, senha, nivel, ativo FROM usuarios WHERE email = ?", (email,))
                    res = cursor.fetchone()
                    conn.close()
                    if res and res[1] == gerar_hash_senha(senha):
                        if res[3] == 1:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario_atual"] = res[0]
                            st.session_state["nivel_acesso"] = res[2]
                            st.success("Login com sucesso!")
                            st.rerun()
                        else:
                            st.warning("Conta por verificar.")
                    else:
                        st.error("Credenciais inválidas.")

            st.markdown("---")
            col_a, col_b = st.columns([3, 1])
            col_a.markdown("Precisa de obter um código de verificação direto?")
            if col_b.button("Receber por E-mail", use_container_width=True):
                st.session_state["modo_recuperacao"] = True
                st.rerun()

        with tab2:
            with st.form("reg"):
                r_nome = st.text_input("Nome Completo")
                r_user = st.text_input("Username")
                r_email = st.text_input("E-mail Corporativo")
                r_senha = st.text_input("Palavra-passe", type="password")
                r_nivel = st.selectbox("Nível", ["Administrador", "Gerente", "Funcionário"])
                cadastrar = st.form_submit_button("Criar Conta")

                if cadastrar:
                    if r_email and r_senha and r_nome:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cod = f"{random.randint(0, 999999):06d}"
                        exp = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
                        try:
                            cursor.execute("INSERT INTO usuarios (nome, username, email, senha, nivel, ativo, codigo_verificacao, codigo_expiracao) VALUES (?, ?, ?, ?, ?, 0, ?, ?)",
                                           (r_nome, r_user, r_email.lower(), gerar_hash_senha(r_senha), r_nivel, cod, exp))
                            conn.commit()
                            conn.close()
                            disparar_emailjs(r_email.lower(), r_nome, cod, "reg")
                            st.session_state["aguardando_verificacao"] = r_email.lower()
                            st.success("Conta criada! Verifique o e-mail.")
                            st.rerun()
                        except Exception as ex:
                            conn.close()
                            st.error(f"Erro ao registar: {ex}")
                    else:
                        st.warning("Preencha todos os campos.")
else:
    st.sidebar.title(f"Bem-vindo, {st.session_state['usuario_atual']}")
    if st.sidebar.button("Terminar Sessão"):
        st.session_state["autenticado"] = False
        st.rerun()
    st.header("Painel Principal - Evolution Gestão Online")
    st.success("Sessão iniciada com sucesso!")
