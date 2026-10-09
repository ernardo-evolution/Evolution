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

  # Migrações seguras e isoladas
  for col_def in [
      ("produtos", "quantidade_estoque", "INTEGER DEFAULT 0"),
      ("produtos", "estoque_minimo", "INTEGER DEFAULT 5"),
      ("clientes", "pais", "TEXT"),
      ("usuarios", "senha", "TEXT"),
      ("usuarios", "ativo", "INTEGER DEFAULT 1"),
      ("usuarios", "codigo_verificacao", "TEXT"),
      ("usuarios", "session_token", "TEXT"),
      ("usuarios", "token_expiry", "TEXT"),
  ]:
    try:
      cursor.execute(f"ALTER TABLE {col_def[0]} ADD COLUMN {col_def[1]} {col_def[2]}")
    except:
      pass

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


# --- 3. MAPEAMENTO DE PAÍSES E MOEDAS ---
PAISES_MOEDAS = {
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português"},
    "Estados Unidos": {
        "moeda": "USD",
        "simbolo": "US$",
        "idioma": "English",
    },
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español"},
}


# --- 4. FUNÇÕES AUXILIARES E DE E-MAIL ---
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


def enviar_email_verificacao(destinatario, codigo):
  # Podes configurar os teus dados SMTP diretamente aqui ou usar st.secrets
  smtp_servidor = "smtp.gmail.com"
  smtp_porta = 587
  # Exemplo usando st.secrets (recomendado no Streamlit Cloud) ou valores fixos de teste
  remetente = st.secrets.get("EMAIL_REMETENTE", "teu_email@gmail.com")
  senha_email = st.secrets.get("EMAIL_SENHA", "tua_senha_de_aplicacao")

  if remetente == "teu_email@gmail.com":
    return False  # SMTP não configurado ainda

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

# --- 5. GESTÃO DE SESSÃO E PERSISTÊNCIA ---
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


# --- 6. BARRA LATERAL ---
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
            t["relatorios"],
            t["tarefas"],
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


# --- 7. INTERFACE PRINCIPAL ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])

  # Se houver um registo a aguardar confirmação de código por e-mail
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
              # Gerar código aleatório de 6 dígitos
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

              # Tentar enviar e-mail
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
                # Caso o SMTP não esteja configurado, exibe o código no ecrã para testes imediatos
                st.session_state["aguardando_verificacao"] = (
                    novo_email.strip()
                )
                st.warning(
                    "⚠️ SMTP não configurado. Para efeitos de teste, o seu"
                    f" código de ativação é: **{codigo_verif}**"
                )
                st.rerun()
          else:
            st.warning("Preencha todos os campos.")

else:
  st.title(t["titulo"])

  # --- MÓDULO: DASHBOARD ---
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
      st.error(f"Erro ao carregar dashboard: {e}")

  # --- MÓDULO: CLIENTES ---
  elif menu == t["clientes"]:
    st.header("👥 Gestão de Clientes")
    with st.form("form_add_cliente"):
      st.subheader("Adicionar Novo Cliente")
      c_nome = st.text_input("Nome do Cliente")
      c_email = st.text_input("E-mail")
      c_tel = st.text_input("Telefone")
      c_pais = st.selectbox("País", list(PAISES_MOEDAS.keys()))
      if st.form_submit_button("Guardar Cliente"):
        if c_nome:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO clientes (nome, email, telefone, pais) VALUES (?, ?,"
              " ?, ?)",
              (c_nome, c_email, c_tel, c_pais),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Novo Cliente",
              f"Cliente {c_nome} registado.",
          )
          st.success("Cliente registado com sucesso!")
          st.rerun()
        else:
          st.warning("O nome do cliente é obrigatório.")

    st.markdown("---")
    st.subheader("Lista de Clientes")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("SELECT id, nome, email, telefone, pais FROM clientes")
      clientes = cursor.fetchall()
      conn.close()
      if clientes:
        for cl in clientes:
          st.markdown(
              f"**ID:** {cl[0]} | **Nome:** {cl[1]} | **E-mail:** {cl[2]} |"
              f" **Telefone:** {cl[3]} | **País:** {cl[4]}"
          )
      else:
        st.info("Nenhum cliente registado.")
    except Exception as e:
      st.error(f"Erro ao listar clientes: {e}")

  # --- MÓDULO: PRODUTOS ---
  elif menu == t["produtos"]:
    st.header("📦 Gestão de Produtos")
    with st.form("form_add_produto"):
      st.subheader("Registar Novo Produto")
      p_nome = st.text_input("Nome do Produto")
      p_preco = st.number_input("Preço Unitário", min_value=0.0, format="%.2f")
      p_qtd = st.number_input("Quantidade em Estoque", min_value=0, value=10)
      p_min = st.number_input("Estoque Mínimo", min_value=0, value=5)
      if st.form_submit_button("Guardar Produto"):
        if p_nome:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO produtos (nome, preco, quantidade_estoque,"
              " estoque_minimo, moeda, simbolo) VALUES (?, ?, ?, ?, ?, ?)",
              (
                  p_nome,
                  p_preco,
                  p_qtd,
                  p_min,
                  emp["moeda"],
                  emp["simbolo"],
              ),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Novo Produto",
              f"Produto {p_nome} adicionado.",
          )
          st.success("Produto registado com sucesso!")
          st.rerun()
        else:
          st.warning("O nome do produto é obrigatório.")
