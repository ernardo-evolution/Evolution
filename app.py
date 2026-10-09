from datetime import datetime
import os
import sqlite3
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online", page_icon="🚀", layout="wide"
)

DB_FILE = "evolution_gestao.db"

# --- INICIALIZAÇÃO SEGURA DA BASE DE DADOS ---
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
            nivel TEXT
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

  # Garantir coluna estoque_minimo se não existir
  try:
    cursor.execute(
        "ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 5"
    )
  except:
    pass

  conn.commit()

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
  st.error(f"Erro ao ligar à base de dados: {db_err}")


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

# --- ESTADOS DA SESSÃO ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
  st.session_state["usuario_atual"] = ""
if "nivel_acesso" not in st.session_state:
  st.session_state["nivel_acesso"] = ""

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


# --- BARRA LATERAL ---
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
      st.session_state["autenticado"] = False
      st.session_state["usuario_atual"] = ""
      st.session_state["nivel_acesso"] = ""
      st.rerun()
  else:
    st.warning("⚠️ Efetue login ou registe uma conta.")


# --- AUTENTICAÇÃO / REGISTO ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])
  tab_login, tab_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])

  with tab_login:
    st.markdown("### Acesso Restrito ao Sistema")
    email_login = st.text_input(
        "E-mail corporativo registado", key="email_l"
    ).strip()
    if st.button("Entrar no Sistema", key="btn_login"):
      if email_login:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome, nivel FROM usuarios WHERE email = ?", (email_login,)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
          st.session_state["autenticado"] = True
          st.session_state["usuario_atual"] = user[0]
          st.session_state["nivel_acesso"] = user[1]
          st.success("Sessão iniciada!")
          st.rerun()
        else:
          st.error(
              "Utilizador não encontrado. Crie uma conta na aba ao lado."
          )
      else:
        st.warning("Introduza o seu e-mail.")

  with tab_registo:
    st.markdown("### Criar Nova Conta")
    with st.form("form_novo_user"):
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
            st.success("Conta criada com sucesso! Já pode fazer login.")
        else:
          st.warning("Preencha todos os campos.")

else:
  st.title(t["titulo"])
  menu = (
      st.session_state.get("menu_ativo", t["dashboard"])
      if "menu_ativo" in st.session_state
      else t["dashboard"]
  )

  # Para garantir que a variável menu da barra lateral funciona perfeitamente:
  # (O radio da sidebar define a variável 'menu' se executado antes)

  # Vamos simplificar e renderizar o dashboard ou secção ativa:
  if "menu" not in locals():
    menu = t["dashboard"]

  if menu == t["dashboard"]:
    st.header("📊 Dashboard Executivo e Operacional")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total) FROM vendas")
    faturamento = cursor.fetchone()[0] or 0.0

    cursor.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status_pedido = 'Em processamento'"
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
