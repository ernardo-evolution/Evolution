from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import secrets
import smtplib
import sqlite3
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ESTILIZAÇÃO VISUAL PROFISSIONAL (TEMA ESCURO GRAFITE) ---
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

# --- 3. MAPEAMENTO DE PAÍSES E MOEDAS (FONTE ÚNICA DA VERDADE) ---
PAISES_MOEDAS = {
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português"},
    "Estados Unidos": {
        "moeda": "USD",
        "simbolo": "US$",
        "idioma": "English",
    },
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español"},
    "Reino Unido": {"moeda": "GBP", "simbolo": "£", "idioma": "English"},
}

# --- 4. INICIALIZAÇÃO E MIGRAÇÃO BLINDADA DA BASE DE DADOS ---
try:
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()

  # Criar tabelas base se não existirem
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
            ativo INTEGER DEFAULT 0,
            codigo_verificacao TEXT,
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

  conn.commit()

  # Função auxiliar robusta para garantir colunas via PRAGMA table_info
  def garantir_coluna(tabela, coluna, definicao):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas_existentes = [col[1] for col in cursor.fetchall()]
    if coluna not in colunas_existentes:
      try:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
        conn.commit()
      except Exception as e:
        print(f"Erro ao adicionar coluna {coluna} em {tabela}: {e}")

  # Executar inspeção e garantia de colunas em todas as tabelas principais
  garantir_coluna("clientes", "pais", "TEXT")
  garantir_coluna("produtos", "quantidade_estoque", "INTEGER DEFAULT 0")
  garantir_coluna("produtos", "estoque_minimo", "INTEGER DEFAULT 5")
  garantir_coluna("produtos", "moeda", "TEXT")
  garantir_coluna("produtos", "simbolo", "TEXT")
  garantir_coluna("usuarios", "senha", "TEXT")
  garantir_coluna("usuarios", "ativo", "INTEGER DEFAULT 1")
  garantir_coluna("usuarios", "codigo_verificacao", "TEXT")
  garantir_coluna("usuarios", "session_token", "TEXT")
  garantir_coluna("usuarios", "token_expiry", "TEXT")
  garantir_coluna("empresa", "pais", "TEXT")
  garantir_coluna("empresa", "moeda", "TEXT")
  garantir_coluna("empresa", "simbolo", "TEXT")

  # Inserir ou corrigir empresa padrão para garantir BRL / R$ se vazio ou incorreto
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
  else:
    cursor.execute("SELECT id, pais, simbolo FROM empresa LIMIT 1")
    emp_db = cursor.fetchone()
    if emp_db and emp_db[1] == "Brasil" and emp_db[2] != "R$":
      cursor.execute("UPDATE empresa SET moeda = 'BRL', simbolo = 'R$' WHERE id = ?", (emp_db[0],))
      conn.commit()

  conn.close()
except Exception as db_err:
  st.error(f"Erro crítico ao inicializar a base de dados: {db_err}")
  st.stop()


# --- 5. FUNÇÕES AUXILIARES E DE E-MAIL ---
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
    print(f"Erro ao carregar empresa: {e}")
  
  return {
      "nome": "Evolution Corp Brasil",
      "pais": "Brasil",
      "pais_registro": "Brasil",
      "moeda": "BRL",
      "simbolo": "R$",
      "idioma": "Português",
      "fuso": "UTC-3",
  }


def enviar_email_verificacao(destinatario, codigo):
  smtp_servidor = "smtp.gmail.com"
  smtp_porta = 587
  remetente = st.secrets.get("EMAIL_REMETENTE", "teu_email@gmail.com")
  senha_email = st.secrets.get("EMAIL_SENHA", "tua_senha_de_aplicacao")

  if remetente == "teu_email@gmail.com":
    return False

  try:
    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Código de Verificação - A Evolution Gestão Online"

    corpo = (
        f"Olá!\n\nO seu código de verificação para ativar a conta no A"
        f" Evolution Gestão Online é: {codigo}\n\nIntroduza este código na"
        " página de confirmação para concluir o registo.\n\nEquipa de"
        " Segurança"
    )
    msg.attach(MIMEText(corpo, "plain"))

    server = smtplib.SMTP(smtp_servidor, smtp_porta)
    server.starttls()
    server.login(remetente, senha_email)
    server.sendmail(remetente, destinatario, msg.as_string())
    server.quit()
    return True
  except Exception as e:
    print(f"Erro ao enviar e-mail: {e}")
    return False


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


t = {
    "titulo": "🚀 A Evolution Gestão Online",
    "dashboard": "Dashboard",
    "clientes": "Clientes",
    "produtos": "Produtos",
    "estoque": "Estoque",
    "vendas": "Vendas",
    "pedidos": "Pedidos",
    "relatorios": "Relatórios",
    "tarefas": "Tarefas",
    "config": "Configurações",
    "sair": "Terminar Sessão",
}

# --- 6. GESTÃO DE SESSÃO E PERSISTÊNCIA ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
  st.session_state["usuario_atual"] = ""
if "nivel_acesso" not in st.session_state:
  st.session_state["nivel_acesso"] = ""
if "aguardando_verificacao" not in st.session_state:
  st.session_state["aguardando_verificacao"] = None

# Verificar token persistente na URL
try:
  query_params = st.query_params
  token_persistencia = query_params.get("session_token", None)

  if not st.session_state["autenticado"] and token_persistencia:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, nivel, token_expiry FROM usuarios WHERE session_token ="
        " ? AND ativo = 1",
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


# --- 7. BARRA LATERAL REFINADA ---
menu = t["dashboard"]
with st.sidebar:
  st.markdown(f"### {emp['nome']}")
  st.markdown("---")
  if st.session_state["autenticado"]:
    st.markdown(
        f"👤 **{st.session_state['usuario_atual']}**  \n🔑 Nível:"
        f" `{st.session_state['nivel_acesso']}`"
    )
    st.markdown("---")
    
    menu = st.radio(
        "Navegação Principal",
        [
            t["dashboard"],
            t["clientes"],
            t["produtos"],
            t["estoque"],
            t["vendas"],
            t["pedidos"],
            t["relatorios"],
            t["tarefas"],
            t["config"],
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("Terminar Sessão", use_container_width=True):
      if "session_token" in st.query_params:
        del st.query_params["session_token"]
      st.session_state["autenticado"] = False
      st.session_state["usuario_atual"] = ""
      st.session_state["nivel_acesso"] = ""
      st.success("Sessão encerrada.")
      st.rerun()
  else:
    st.warning("⚠️ Efetue login para aceder ao sistema.")


# --- 8. INTERFACE PRINCIPAL ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])

  if st.session_state["aguardando_verificacao"]:
    st.warning(
        "🔒 Conta pendente de ativação. Enviámos um código de 6 dígitos para o"
        f" seu e-mail: **{st.session_state['aguardando_verificacao']}**"
    )
    with st.form("form_verificar_codigo"):
      codigo_inserido = st.text_input(
          "Introduza o Código de Verificação", max_chars=6
      )
      btn_confirmar = st.form_submit_button("Confirmar e Ativar Conta")

      if btn_confirmar:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE email = ? AND codigo_verificacao = ?",
            (
                st.session_state["aguardando_verificacao"],
                codigo_inserido.strip(),
            ),
        )
        res = cursor.fetchone()
        if res:
          cursor.execute(
              "UPDATE usuarios SET ativo = 1, codigo_verificacao = NULL WHERE"
              " email = ?",
              (st.session_state["aguardando_verificacao"],),
          )
          conn.commit()
          conn.close()
          st.success("Conta verificada e ativada com sucesso! Já pode fazer login.")
          st.session_state["aguardando_verificacao"] = None
          st.rerun()
        else:
          conn.close()
          st.error("Código incorreto. Tente novamente.")
  else:
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
                "SELECT id, nome, nivel, ativo FROM usuarios WHERE email = ?",
                (email_login,),
            )
            user = cursor.fetchone()

            if user:
              user_id, nome_u, nivel_u, ativo_u = user
              if ativo_u == 0:
                conn.close()
                st.error(
                    "Esta conta ainda não foi ativada por e-mail. Contacte o"
                    " suporte."
                )
              else:
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = nome_u
                st.session_state["nivel_acesso"] = nivel_u

                if lembrar_sessao:
                  token = secrets.token_hex(32)
                  expiry = (datetime.now() + timedelta(days=30)).strftime(
                      "%Y-%m-%d %H:%M:%S"
                  )
                  cursor.execute(
                      "UPDATE usuarios SET session_token = ?, token_expiry ="
                      " ? WHERE id = ?",
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
                  "Utilizador não encontrado. Crie uma conta na aba ao lado."
              )
          else:
            st.warning("Introduza o seu e-mail.")

    with tab_registo:
      st.markdown("### Criar Nova Conta com Verificação Segura")
      with st.form("form_reg_main"):
        novo_nome = st.text_input("Nome Completo")
        novo_email = st.text_input("E-mail Corporativo")
        novo_nivel = st.selectbox(
            "Nível de Acesso", ["Administrador", "Gerente", "Funcionário"]
        )
        if st.form_submit_button("Registar e Enviar Código"):
          if novo_nome and novo_email:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = ?", (novo_email.strip(),)
            )
            existe = cursor.fetchone()
            if existe:
              st.error("Este e-mail já está registado.")
              conn.close()
            else:
              codigo_verif = str(random.randint(100000, 999999))
              cursor.execute(
                  "INSERT INTO usuarios (nome, email, nivel, ativo,"
                  " codigo_verificacao) VALUES (?, ?, ?, 0, ?)",
                  (
                      novo_nome.strip(),
                      novo_email.strip(),
                      novo_nivel,
                      codigo_verif,
                  ),
              )
              conn.commit()
              conn.close()

              enviou = enviar_email_verificacao(
                  novo_email.strip(), codigo_verif
              )
              if enviou:
                st.session_state["aguardando_verificacao"] = (
                    novo_email.strip()
                )
                st.success(
                    "Registo efetuado! Verifique o código enviado para o seu"
                    " e-mail."
                )
                st.rerun()
              else:
                st.session_state["aguardando_verificacao"] = (
