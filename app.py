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
            entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
        if entrar:
            st.session_state["email_input"] = email
            if email and senha:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT nome, nivel, senha, email FROM usuarios WHERE email = ?", (email,))
                user = cursor.fetchone()
                conn.close()
                
                if user and user[2] == gerar_hash_senha(senha):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = user[0]
                    st.session_state["nivel_acesso"] = user[1]
                    st.session_state["email_atual"] = user[3]
                    
                    if lembrar:
                        st.query_params["email"] = user[3]
                        
                    registar_log(user[0], user[3], "Login", "Sessão iniciada com sucesso", "Sucesso")
                    st.success("Sessão iniciada com sucesso!")
                    st.rerun()
                else:
                    registar_log("Desconhecido", email, "Login", "Tentativa com credenciais inválidas", "Falha")
                    st.error("E-mail ou palavra-passe incorretos.")
            else:
                st.warning("Preencha todos os campos.")
                    
    with tab2:
        st.markdown("### Criar Conta Corporativa")
        with st.form("form_registo"):
            r_nome = st.text_input("Nome Completo *")
            r_user = st.text_input("Username *")
            r_email = st.text_input("E-mail Corporativo *")
            r_senha = st.text_input("Palavra-passe (mín. 6 caracteres) *", type="password")
            r_nivel = st.selectbox("Nível de Acesso", ["Administrador", "Gerente", "Funcionário"])
            registar = st.form_submit_button("Criar Conta", use_container_width=True)
            
        if registar:
            if r_nome and r_email and r_senha and r_user:
                if len(r_senha) < 6:
                    st.error("A palavra-passe deve ter pelo menos 6 caracteres.")
                else:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM usuarios WHERE email = ? OR username = ?", (r_email.lower(), r_user.strip()))
                    if cursor.fetchone():
                        conn.close()
                        registar_log(r_nome, r_email, "Registo", "Tentativa com e-mail/username duplicado", "Falha")
                        st.error("Este e-mail ou username já se encontra registado.")
                    else:
                        cursor.execute(
                            "INSERT INTO usuarios (nome, username, email, senha, nivel, ativo) VALUES (?, ?, ?, ?, ?, 1)",
                            (r_nome.strip(), r_user.strip(), r_email.lower(), gerar_hash_senha(r_senha), r_nivel)
                        )
                        conn.commit()
                        conn.close()
                        registar_log(r_nome.strip(), r_email.lower(), "Registo", "Nova conta criada com sucesso", "Sucesso")
                        st.success("Conta criada com sucesso! Vá à aba 'Iniciar Sessão' para entrar.")
            else:
                st.warning("Preencha todos os campos obrigatórios (*).")

# --- 7. PAINEL DE GESTÃO E MÓDULOS OPERACIONAIS ---
else:
    conn = sqlite3.connect(DB_FILE)
    
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Executivo")
        st.markdown(f"Bem-vindo(a) de volta, **{st.session_state['usuario_atual']}**! Aqui tens o resumo geral do teu negócio.")
        st.markdown("---")
        
        try:
            df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
            df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
            df_produtos = pd.read_sql_query("SELECT * FROM produtos", conn)
            
            total_faturamento = df_vendas["valor_total"].sum() if not df_vendas.empty else 0.0
            total_vendas = len(df_vendas)
            total_clientes = len(df_clientes)
            total_produtos = len(df_produtos)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
            c2.metric("Total de Vendas", total_vendas)
            c3.metric("Clientes Registados", total_clientes)
            c4.metric("Produtos Cadastrados", total_produtos)
            
            st.markdown("---")
            if not df_vendas.empty:
                st.subheader("📈 Evolução de Vendas")
                st.bar_chart(df_vendas, x="data_venda", y="valor_total")
            else:
                st.info("Ainda não existem vendas registadas para gerar gráficos.")
        except Exception as e:
            st.error(f"Erro ao carregar dados do dashboard: {e}")

    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        
        with st.form("form_cliente"):
            c_nome = st.text_input("Nome do Cliente")
            c_email = st.text_input("E-mail")
            c_tel = st.text_input("Telefone")
            c_cid = st.text_input("Cidade")
            btn_add_c = st.form_submit_button("Adicionar Cliente")
            
        if btn_add_c and c_nome:
            cursor = conn.cursor()
            data_cad = datetime.now().strftime("%d/%m/%Y")
            cursor.execute("INSERT INTO clientes (nome, email, telefone, cidade, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                           (c_nome, c_email, c_tel, c_cid, data_cad))
            conn.commit()
            msg_log = f"Cliente {c_nome} adicionado"
            registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Cliente", msg_log, "Sucesso")
            st.success(f"Cliente '{c_nome}' adicionado com sucesso!")
            st.rerun()
                
        st.markdown("---")
        st.subheader("Lista de Clientes")
        df_cli = pd.read_sql_query("SELECT id, nome, email, telefone, cidade, data_cadastro FROM clientes", conn)
        st.dataframe(df_cli, use_container_width=True)

    elif menu == "📦 Produtos & Stock":
        st.header("📦 Gestão de Produtos e Stock")
        
        with st.form("form_produto"):
            p_nome = st.text_input("Nome do Produto")
            p_preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
            p_stock = st.number_input("Quantidade em Stock", min_value=0, step=1)
            btn_add_p = st.form_submit_button("Guardar Produto")
            
        if btn_add_p and p_nome:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produtos (nome, preco, stock) VALUES (?, ?, ?)", (p_nome, p_preco, p_stock))
            conn.commit()
            msg_log = f"Produto {p_nome} criado"
            registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Produto", msg_log, "Sucesso")
            st.success(f"Produto '{p_nome}' registado com sucesso!")
            st.rerun()
                
        st.markdown("---")
        st.subheader("Catálogo Atual")
        df_prod = pd.read_sql_query("SELECT id, nome, preco, stock FROM produtos", conn)
        st.dataframe(df_prod, use_container_width=True)

    elif menu == "🛒 Vendas":
        st.header("🛒 Registar Venda")
        
        df_cli = pd.read_sql_query("SELECT nome FROM clientes", conn)
        df_prod = pd.read_sql_query("SELECT nome, preco FROM produtos", conn)
        
        if df_cli.empty or df_prod.empty:
            st.warning("⚠️ Precisa de registar pelo menos um cliente e um produto antes de efetuar vendas.")
        else:
            with st.form("form_venda"):
                v_cliente = st.selectbox("Cliente", df_cli["nome"].tolist())
                v_produto = st.selectbox("Produto", df_prod["nome"].tolist())
                v_qtd = st.number_input("Quantidade", min_value=1, step=1)
                btn_finalizar = st.form_submit_button("Finalizar Venda")
                
            if btn_finalizar:
                preco_unit = df_prod.loc[df_prod["nome"] == v_produto, "preco"].values[0]
                total = preco_unit * v_qtd
                data_v = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                cursor = conn.cursor()
                cursor.execute("INSERT INTO vendas (cliente, produto, quantidade, valor_total, data_venda) VALUES (?, ?, ?, ?, ?)",
                               (v_cliente, v_produto, v_qtd, total, data_v))
                conn.commit()
                msg_log = f"Venda de {v_qtd}x {
