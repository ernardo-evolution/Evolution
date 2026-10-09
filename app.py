from datetime import datetime, timedelta
import os
import secrets
import sqlite3
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA (PRIMEIRA INSTRUÇÃO OBRIGATÓRIA) ---
st.set_page_config(
    page_title="A Evolution Gestão Online", page_icon="🚀", layout="wide"
)

DB_FILE = "evolution_gestao.db"

# --- 2. INICIALIZAÇÃO SEGURA DA BASE DE DADOS ---
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
            email TEXT,
            senha TEXT,
            nivel TEXT,
            session_token TEXT,
            token_expiry TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            pais TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco REAL,
            quantidade_estoque INTEGER,
            estoque_minimo INTEGER,
            moeda TEXT,
            simbolo TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            valor_total REAL,
            moeda_original TEXT,
            data_hora TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto TEXT,
            quantidade INTEGER,
            status_venda TEXT,
            status_separacao TEXT,
            status_envio TEXT,
            status_pedido TEXT,
            data_criacao TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            responsavel TEXT,
            prazo TEXT,
            prioridade TEXT,
            status TEXT,
            relacionamento TEXT,
            data_criacao TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            acao TEXT,
            detalhes TEXT,
            data_hora TEXT
        )
    """)

  # Garantir colunas essenciais na tabela produtos dinamicamente
  cursor.execute("PRAGMA table_info(produtos)")
  col_prods = [c[1] for c in cursor.fetchall()]
  if "quantidade_estoque" not in col_prods:
    cursor.execute(
        "ALTER TABLE produtos ADD COLUMN quantidade_estoque INTEGER DEFAULT 0"
    )
  if "estoque_minimo" not in col_prods:
    cursor.execute(
        "ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 5"
    )

  # Garantir colunas na tabela usuarios
  cursor.execute("PRAGMA table_info(usuarios)")
  col_users = [c[1] for c in cursor.fetchall()]
  for col_nec in ["senha", "session_token", "token_expiry"]:
    if col_nec not in col_users:
      cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {col_nec} TEXT")

  conn.commit()

  # Inserir empresa padrão se vazio
  cursor.execute("SELECT COUNT(*) FROM empresa")
  if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo,"
        " idioma, fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "Evolution Corp Brasil",
            "Brasil",
            "Brasil",
            "BRL",
            "R$",
            "Português",
            "UTC-3",
        ),
    )
    conn.commit()

  conn.close()
except Exception as db_err:
  st.error(f"Erro crítico ao inicializar a base de dados: {db_err}")
  st.stop()


# --- 3. FUNÇÕES AUXILIARES ---
def carregar_empresa():
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, pais, pais_registro, moeda, simbolo, idioma, fuso FROM"
        " empresa LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    if row:
      return {
          "nome": row[0],
          "pais": row[1],
          "pais_registro": row[2],
          "moeda": row[3],
          "simbolo": row[4],
          "idioma": row[5],
          "fuso": row[6],
      }
  except:
    pass
  return {
      "nome": "Evolution Corp Brasil",
      "pais": "Brasil",
      "pais_registro": "Brasil",
      "moeda": "BRL",
      "simbolo": "R$",
      "idioma": "Português",
      "fuso": "UTC-3",
  }


def registrar_historico(usuario, acao, detalhes):
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(
        "INSERT INTO historico (usuario, acao, detalhes, data_hora) VALUES (?,"
        " ?, ?, ?)",
        (usuario, acao, detalhes, data_hora),
    )
    conn.commit()
    conn.close()
  except:
    pass


PAISES_MOEDAS = {
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português"},
    "Estados Unidos": {"moeda": "USD", "simbolo": "US$", "idioma": "English"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português"},
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español"},
}

t = {
    "titulo": "🚀 A Evolution Gestão Online",
    "dashboard": "Dashboard",
    "clientes": "Clientes",
    "produtos": "Produtos",
    "estoque": "Estoque",
    "vendas": "Vendas",
    "pedidos": "Pedidos",
    "enviados": "Produtos Enviados",
    "relatorios": "Relatórios",
    "tarefas": "Tarefas",
    "mya": "MyA (Assistente IA)",
    "config": "Configurações",
    "sair": "Terminar Sessão",
}

# --- 4. GESTÃO DE SESSÃO E PERSISTÊNCIA ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
  st.session_state["usuario_atual"] = ""
if "nivel_acesso" not in st.session_state:
  st.session_state["nivel_acesso"] = ""

# Verificar token persistente na URL
try:
  query_params = st.query_params
  token_persistencia = query_params.get("session_token", None)

  if not st.session_state["autenticado"] and token_persistencia:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, nivel, token_expiry FROM usuarios WHERE session_token ="
        " ?",
        (token_persistencia,),
    )
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
      nome_u, nivel_u, expiry_str = user_data
      if expiry_str:
        expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expiry_dt:
          st.session_state["autenticado"] = True
          st.session_state["usuario_atual"] = nome_u
          st.session_state["nivel_acesso"] = nivel_u
except Exception:
  pass

emp = carregar_empresa()
simbolo_ativo = emp["simbolo"]


def formatar_moeda(valor):
  try:
    v = float(valor)
  except:
    v = 0.0
  return f"{simbolo_ativo} {v:,.2f}".replace(",", "X").replace(".", ",").replace(
      "X", "."
  )


# --- 5. BARRA LATERAL ---
menu = t["dashboard"]
with st.sidebar:
  if st.session_state["autenticado"]:
    st.info(
        f"👤 Utilizador: **{st.session_state['usuario_atual']}**\n🔑 Nível:"
        f" **{st.session_state['nivel_acesso']}**"
    )
    st.markdown("---")
    menu = st.radio(
        "Navegação",
        [
            t["dashboard"],
            t["clientes"],
            t["produtos"],
            t["estoque"],
            t["vendas"],
            t["pedidos"],
            t["enviados"],
            t["relatorios"],
            t["tarefas"],
            t["mya"],
            t["config"],
        ],
    )
    st.markdown("---")
    if st.button(t["sair"]):
      if "session_token" in st.query_params:
        del st.query_params["session_token"]
      st.session_state["autenticado"] = False
      st.session_state["usuario_atual"] = ""
      st.session_state["nivel_acesso"] = ""
      st.success("Sessão encerrada.")
      st.rerun()
  else:
    st.warning("⚠️ Efetue login para aceder.")


# --- 6. INTERFACE PRINCIPAL ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])
  tab_login, tab_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])

  with tab_login:
    st.markdown("### Acesso Restrito ao Sistema")
    with st.form("form_login_main"):
      email_login = st.text_input("E-mail corporativo").strip()
      lembrar_sessao = st.checkbox("Lembrar de mim neste dispositivo")
      btn_entrar = st.form_submit_button("Entrar no Sistema")

      if btn_entrar:
        if email_login:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id, nome, nivel FROM usuarios WHERE email = ?",
              (email_login,),
          )
          user = cursor.fetchone()

          if user:
            user_id, nome_u, nivel_u = user
            st.session_state["autenticado"] = True
            st.session_state["usuario_atual"] = nome_u
            st.session_state["nivel_acesso"] = nivel_u

            if lembrar_sessao:
              token = secrets.token_hex(32)
              expiry = (datetime.now() + timedelta(days=30)).strftime(
                  "%Y-%m-%d %H:%M:%S"
              )
              cursor.execute(
                  "UPDATE usuarios SET session_token = ?, token_expiry = ? WHERE"
                  " id = ?",
                  (token, expiry, user_id),
              )
              conn.commit()
              st.query_params["session_token"] = token

            conn.close()
            st.success("Sessão iniciada!")
            st.rerun()
          else:
            conn.close()
            st.error(
                "Utilizador não encontrado. Verifique o e-mail ou crie uma conta"
                " na aba ao lado."
            )
        else:
          st.warning("Introduza o seu e-mail.")

  with tab_registo:
    st.markdown("### Criar Nova Conta")
    with st.form("form_reg_main"):
      novo_nome = st.text_input("Nome Completo")
      novo_email = st.text_input("E-mail Corporativo")
      novo_nivel = st.selectbox(
          "Nível de Acesso", ["Administrador", "Gerente", "Funcionário"]
      )
      if st.form_submit_button("Registar Conta"):
        if novo_nome and novo_email:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id FROM usuarios WHERE email = ?", (novo_email.strip(),)
          )
          existe = cursor.fetchone()
          if existe:
            st.error("Este e-mail já está registado.")
          else:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, nivel) VALUES (?, ?, ?)",
                (novo_nome.strip(), novo_email.strip(), novo_nivel),
            )
            conn.commit()
            conn.close()
            st.success("Conta criada com sucesso! Já pode iniciar sessão.")
        else:
          st.warning("Preencha todos os campos.")

else:
  st.title(t["titulo"])

  if menu == t["dashboard"]:
    st.header("📊 Dashboard Executivo e Operacional")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("SELECT SUM(valor_total) FROM vendas")
      faturamento = cursor.fetchone()[0] or 0.0

      cursor.execute(
          "SELECT COUNT(*) FROM pedidos WHERE status_pedido = 'Em"
          " processamento'"
      )
      ped_proc = cursor.fetchone()[0] or 0

      cursor.execute(
          "SELECT COUNT(*) FROM pedidos WHERE status_separacao = 'Pendente'"
      )
      ped_pend = cursor.fetchone()[0] or 0

      cursor.execute(
          "SELECT COUNT(*) FROM produtos WHERE quantidade_estoque <="
          " estoque_minimo"
      )
      est_baixo = cursor.fetchone()[0] or 0
      conn.close()

      c1, c2, c3, c4 = st.columns(4)
      c1.metric("Faturamento Total", formatar_moeda(faturamento))
      c2.metric("Pedidos Pendentes", ped_pend)
      c3.metric("Em Processamento", ped_proc)
      c4.metric("Estoque Baixo", est_baixo, delta_color="inverse")
    except Exception as e:
      st.error(f"Erro ao carregar dados do dashboard: {e}")
