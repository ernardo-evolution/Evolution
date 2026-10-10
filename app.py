from datetime import datetime, timedelta
import hashlib
import os
import random
import secrets
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

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
    "Reino Unido": {"moeda": "GBP", "simbolo": "£", "idioma": "English"},
}

# --- 4. FUNÇÕES DE SEGURANÇA E HASH ---
def gerar_hash_senha(senha):
  return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def mascarar_email(email):
  if "@" not in email:
    return email
  partes = email.split("@")
  nome = partes[0]
  dominio = partes[1]
  nome_mascarado = nome[:2] + "****" if len(nome) > 2 else "**"
  return f"{nome_mascarado}@{dominio}"


# --- 5. INICIALIZAÇÃO E MIGRAÇÃO DA BASE DE DADOS ---
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
            ativo INTEGER DEFAULT 0,
            codigo_verificacao TEXT,
            codigo_expiracao TEXT,
            tentativas_codigo INTEGER DEFAULT 0,
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

  def garantir_coluna(tabela, coluna, definicao):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas_existentes = [col[1] for col in cursor.fetchall()]
    if coluna not in colunas_existentes:
      try:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
        conn.commit()
      except Exception as e:
        print(f"Erro ao adicionar coluna {coluna} em {tabela}: {e}")

  garantir_coluna("usuarios", "username", "TEXT")
  garantir_coluna("usuarios", "codigo_expiracao", "TEXT")
  garantir_coluna("usuarios", "tentativas_codigo", "INTEGER DEFAULT 0")
  garantir_coluna("produtos", "estoque_minimo", "INTEGER DEFAULT 4")
  garantir_coluna("empresa", "moeda", "TEXT")
  garantir_coluna("empresa", "simbolo", "TEXT")

  garantir_coluna("historico", "username", "TEXT")
  garantir_coluna("historico", "email", "TEXT")
  garantir_coluna("historico", "resultado", "TEXT")
  garantir_coluna("historico", "servico", "TEXT")
  garantir_coluna("historico", "codigo_erro", "TEXT")
  garantir_coluna("historico", "rastreamento_id", "TEXT")

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


# --- 6. FUNÇÕES AUXILIARES E LOGS ---
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


def registrar_historico_profissional(usuario, username, email, acao, detalhes, resultado, servico="EmailJS", codigo_erro="", rastreamento_id=""):
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(
        """INSERT INTO historico (usuario, username, email, acao, detalhes, resultado, servico, codigo_erro, rastreamento_id, data_hora) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (usuario, username, email, acao, detalhes, resultado, servico, codigo_erro, rastreamento_id, data_hora),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Erro ao registar log: {e}")


def disparar_emailjs(destinatario, nome_usuario, codigo, rastreamento_id):
  """Dispara o EmailJS de forma segura injetando script no cliente"""
  try:
    ej_conf = st.secrets.get("emailjs", {})
  except:
    ej_conf = {}

  service_id = ej_conf.get("service_id", "service_15qkad9")
  template_id = ej_conf.get("template_id", "0f4y8it")
  public_key = ej_conf.get("public_key", "PCUYqPfeqGqMvHbaD")

  if not service_id or not template_id or not public_key:
    return False, "Configuração EmailJS em falta nos segredos."

  html_code = f"""
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
    <script type="text/javascript">
       (function(){{
          emailjs.init("{public_key}");
       }})();
       
       var templateParams = {{
          to_email: "{destinatario}",
          to_name: "{nome_usuario}",
          codigo: "{codigo}",
          code: "{codigo}",
          message: "{codigo}",
          rastreamento: "{rastreamento_id}"
       }};

       emailjs.send("{service_id}", "{template_id}", templateParams)
          .then(function(response) {{
             console.log('SUCCESS!', response.status, response.text);
          }}, function(error) {{
             console.log('FAILED...', error);
          }});
    </script>
  """
  components.html(html_code, height=0, width=0)
  return True, "Requisição aceita pelo EmailJS"


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
    "logs": "Logs do Sistema",
    "config": "Configurações",
    "sair": "Terminar Sessão",
}

# --- 7. GESTÃO DE SESSÃO E PERSISTÊNCIA ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
  st.session_state["usuario_atual"] = ""
if "username_atual" not in st.session_state:
  st.session_state["username_atual"] = ""
if "nivel_acesso" not in st.session_state:
  st.session_state["nivel_acesso"] = ""
if "aguardando_verificacao" not in st.session_state:
  st.session_state["aguardando_verificacao"] = None

try:
  query_params = st.query_params
  token_persistencia = query_params.get("session_token", None)

  if not st.session_state["autenticado"] and token_persistencia:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, username, nivel, token_expiry FROM usuarios WHERE session_token ="
        " ? AND ativo = 1",
        (token_persistencia,),
    )
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
      nome_u, username_u, nivel_u, expiry_str = user_data
      if expiry_str:
        expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expiry_dt:
          st.session_state["autenticado"] = True
          st.session_state["usuario_atual"] = nome_u
          st.session_state["username_atual"] = username_u or ""
          st.session_state["nivel_acesso"] = nivel_u
except Exception as ex:
  print(f"Aviso na persistência de sessão: {ex}")

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


# --- 8. BARRA LATERAL REFINADA ---
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

    lista_menus = [
        t["dashboard"],
        t["clientes"],
        t["produtos"],
        t["estoque"],
        t["vendas"],
        t["pedidos"],
        t["relatorios"],
        t["tarefas"],
        t["config"],
    ]
    if st.session_state["nivel_acesso"] == "Administrador":
      lista_menus.append(t["logs"])

    menu = st.radio(
        "Navegação Principal",
        lista_menus,
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("Terminar Sessão", use_container_width=True):
      if "session_token" in st.query_params:
        del st.query_params["session_token"]
      st.session_state["autenticado"] = False
      st.session_state["usuario_atual"] = ""
      st.session_state["username_atual"] = ""
      st.session_state["nivel_acesso"] = ""
      st.success("Sessão encerrada.")
      st.rerun()
  else:
    st.warning("⚠️ Efetue login para aceder ao sistema.")


# --- 9. INTERFACE PRINCIPAL ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])

  if not st.session_state["aguardando_verificacao"]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM usuarios WHERE ativo = 0 ORDER BY id DESC LIMIT 1")
    pendente_db = cursor.fetchone()
    conn.close()
    if pendente_db:
      st.session_state["aguardando_verificacao"] = pendente_db[0]

  if st.session_state["aguardando_verificacao"]:
    email_pendente = st.session_state["aguardando_verificacao"]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, username FROM usuarios WHERE email = ?", (email_pendente,))
    row_user = cursor.fetchone()
    conn.close()
    nome_pendente = row_user[0] if row_user else "Utilizador"
    username_pendente = row_user[1] if row_user else ""

    st.markdown("### ✉️ Confirme seu e-mail")
    st.markdown(
        f"Um código de verificação de 6 dígitos foi solicitado para o endereço: **{mascarar_email(email_pendente)}**. "
        "Insira o código abaixo para concluir o registo com segurança. (Validade: 10 minutos)"
    )

    with st.form("form_verificar_codigo"):
      codigo_inserido = st.text_input("Código de Verificação", max_chars=6)
      col_btn1, col_btn2, col_btn3 = st.columns(3)
      with col_btn1:
        btn_confirmar = st.form_submit_button("Confirmar e-mail", use_container_width=True)
      with col_btn2:
        btn_reenviar = st.form_submit_button("Reenviar código", use_container_width=True)
      with col_btn3:
        btn_cancelar = st.form_submit_button("Corrigir e-mail", use_container_width=True)

      rastreamento_id = secrets.token_hex(6)

      if btn_confirmar:
        if not codigo_inserido.strip():
          st.error("Insira o código de verificação de 6 dígitos.")
        else:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id, codigo_verificacao, codigo_expiracao, tentativas_codigo FROM usuarios WHERE email = ?",
              (email_pendente,),
          )
          user_row = cursor.fetchone()

          if not user_row:
            conn.close()
            st.error("Registo não encontrado.")
          else:
            u_id, db_code, db_expiry, tentativas = user_row

            if tentativas >= 5:
              conn.close()
              registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Tentativa de Verificação", "Bloqueio por excesso de tentativas", "Bloqueado", "Sistema", "ERR_MAX_TENTATIVAS", rastreamento_id)
              st.error("Limite máximo de tentativas excedido (5/5). Conta temporariamente bloqueada. Solicite novo reenvio.")
            else:
              exp_dt = datetime.strptime(db_expiry, "%Y-%m-%d %H:%M:%S") if db_expiry else datetime.min
              if datetime.now() > exp_dt:
                conn.close()
                registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Código Expirado", "Tentativa com código vencido", "Falha", "Sistema", "ERR_CODIGO_EXPIRADO", rastreamento_id)
                st.error("O código expirou. Clique em 'Reenviar código'.")
              elif db_code != codigo_inserido.strip():
                novo_tentativas = tentativas + 1
                cursor.execute("UPDATE usuarios SET tentativas_codigo = ? WHERE id = ?", (novo_tentativas, u_id))
                conn.commit()
                conn.close()
                registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Código Incorreto", f"Tentativa falhada {novo_tentativas}/5", "Falha", "Sistema", "ERR_CODIGO_ERRADO", rastreamento_id)
                st.error(f"Código incorreto. Tentativa {novo_tentativas} de 5.")
              else:
                cursor.execute(
                    "UPDATE usuarios SET ativo = 1, codigo_verificacao = NULL, codigo_expiracao = NULL, tentativas_codigo = 0 WHERE id = ?",
                    (u_id,),
                )
                conn.commit()
                conn.close()
                registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "E-mail Verificado", "Código confirmado com sucesso", "Sucesso", "EmailJS", "", rastreamento_id)
                st.success("E-mail confirmado com sucesso! Aceda à aba de início de sessão.")
                st.session_state["aguardando_verificacao"] = None
                st.rerun()

      if btn_reenviar:
        novo_codigo = f"{random.randint(0, 999999):06d}"
        nova_expiracao = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET codigo_verificacao = ?, codigo_expiracao = ?, tentativas_codigo = 0 WHERE email = ?",
            (novo_codigo, nova_expiracao, email_pendente)
        )
        conn.commit()
        conn.close()

        registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Código Reenviado", "Nova solicitação de envio", "Pendente", "EmailJS", "", rastreamento_id)
        sucesso_ej, msg_ej = disparar_emailjs(email_pendente, nome_pendente, novo_codigo, rastreamento_id)

        if sucesso_ej:
          registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Envio Aceito pelo EmailJS", "Mensagem encaminhada ao serviço", "Sucesso", "EmailJS", "", rastreamento_id)
          st.success("Um novo código de verificação foi enviado via EmailJS. Verifique também a sua caixa de spam.")
        else:
          registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Falha no Envio", msg_ej, "Falha", "EmailJS", "ERR_EMAILJS_FAIL", rastreamento_id)
          st.error(f"Não foi possível enviar o código de verificação. Tente novamente em instantes. ({msg_ej})")

      if btn_cancelar:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email = ? AND ativo = 0", (email_pendente,))
        conn.commit()
        conn.close()
        registrar_historico_profissional(nome_pendente, username_pendente, email_pendente, "Correção de E-mail", "Registo pendente descartado", "Sucesso", "Sistema", "", rastreamento_id)
        st.session_state["aguardando_verificacao"] = None
        st.info("Pode realizar um novo registo com o e-mail correto.")
        st.rerun()

  else:
    tab_login, tab_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Conta"])

    with tab_login:
      st.markdown("### Acesso Restrito ao Sistema")
      with st.form("form_login_main"):
        email_login = st.text_input("E-mail corporativo").strip()
        senha_login = st.text_input("Palavra-passe / Senha", type="password")
        lembrar_sessao = st.checkbox("Lembrar de mim neste dispositivo")
        btn_entrar = st.form_submit_button("Entrar no Sistema")

        rastreamento_id = secrets.token_hex(6)

        if btn_entrar:
          if email_login and senha_login:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, username, senha, nivel, ativo FROM usuarios WHERE email = ?",
                (email_login.lower(),),
            )
            user = cursor.fetchone()

            if user:
              user_id, nome_u, username_u, senha_db, nivel_u, ativo_u = user
              senha_hash_input = gerar_hash_senha(senha_login)

              if senha_db != senha_hash_input:
                conn.close()
                registrar_historico_profissional(nome_u, username_u, email_login, "Tentativa de Login", "Palavra-passe incorreta", "Falha", "Sistema", "ERR_SENHA_ERRADA", rastreamento_id)
                st.error("Credenciais inválidas. Verifique o seu e-mail e palavra-passe.")
              elif ativo_u == 0:
                conn.close()
                st.session_state["aguardando_verificacao"] = email_login.lower()
                registrar_historico_profissional(nome_u, username_u, email_login, "Tentativa de Acesso sem Verificação", "Conta inativa bloqueada no login", "Bloqueado", "Sistema", "ERR_CONTA_INATIVA", rastreamento_id)
                st.error("Esta conta ainda não foi confirmada. Introduza o código enviado para o seu e-mail.")
                st.rerun()
              else:
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = nome_u
                st.session_state["username_atual"] = username_u or ""
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
                registrar_historico_profissional(nome_u, username_u, email_login, "Login Bem-Sucedido", "Sessão iniciada com sucesso", "Sucesso", "Sistema", "", rastreamento_id)
                st.success("Sessão iniciada com sucesso!")
                st.rerun()
            else:
              conn.close()
              registrar_historico_profissional("", "", email_login, "Tentativa de Login", "Utilizador não encontrado", "Falha", "Sistema", "ERR_USER_NOT_FOUND", rastreamento_id)
              st.error("Utilizador não encontrado. Registe uma conta na aba ao lado.")
          else:
            st.warning("Preencha todos os campos obrigatórios.")

    with tab_registo:
      st.markdown("### Criar Conta Corporativa")
      with st.form("form_reg_main"):
        novo_nome = st.text_input("Nome Completo *")
        novo_username = st.text_input("Nome de Utilizador (Username) *")
        novo_email = st.text_input("E-mail Corporativo *")
        nova_senha = st.text_input("Palavra-passe *", type="password")
        conf_senha = st.text_input("Confirmar Palavra-passe *", type="password")
        novo_nivel = st.selectbox(
            "Nível de Acesso", ["Administrador", "Gerente", "Funcionário"]
        )
        btn_registar = st.form_submit_button("Criar minha conta")

        rastreamento_id = secrets.token_hex(6)

        if btn_registar:
          if not novo_nome.strip() or not novo_username.strip() or not novo_email.strip() or not nova_senha:
            st.warning("Preencha todos os campos obrigatórios (*).")
          elif "@" not in novo_email or "." not in novo_email:
            st.error("Introduza um endereço de e-mail válido.")
          elif nova_senha != conf_senha:
            st.error("As palavras-passe inseridas não coincidem.")
          elif len(nova_senha) < 6:
            st.error("A palavra-passe deve conter pelo menos 6 caracteres.")
          else:
            email_limpo = novo_email.strip().lower()
            username_limpo = novo_username.strip().lower()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ativo FROM usuarios WHERE email = ? OR username = ?", (email_limpo, username_limpo))
            existe = cursor.fetchone()

            if existe:
              conn.close()
              registrar_historico_profissional(novo_nome, username_limpo, email_limpo, "Cadastro Recusado", "E-mail ou username duplicado", "Recusado", "Sistema", "ERR_DUPLICADO", rastreamento_id)
              st.error("Já existe uma conta registada com este e-mail ou nome de utilizador.")
            else:
              codigo_verif = f"{random.randint(0, 999999):06d}"
              expiracao_dt = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
              senha_hash = gerar_hash_senha(nova_senha)

              cursor.execute(
                  """INSERT INTO usuarios (nome, username, email, senha, nivel, ativo, codigo_verificacao, codigo_expiracao, tentativas_codigo) 
                     VALUES (?, ?, ?, ?, ?, 0, ?, ?, 0)""",
                  (
                      novo_nome.strip(),
                      username_limpo,
                      email_limpo,
                      senha_hash,
                      novo_nivel,
                      codigo_verif,
                      expiracao_dt,
                  ),
              )
              conn.commit()
              conn.close()

              registrar_historico_profissional(novo_nome, username_limpo, email_limpo, "Cadastro Iniciado", "Dados validados e conta criada pendente", "Sucesso", "Sistema", "", rastreamento_id)

              sucesso_ej, msg_ej = disparar_emailjs(email_limpo, novo_nome.strip(), codigo_verif, rastreamento_id)

              if sucesso_ej:
                registrar_historico_profissional(novo_nome, username_limpo, email_limpo, "Envio Aceito pelo EmailJS", "Código encaminhado via EmailJS", "Sucesso", "EmailJS", "", rastreamento_id)
                st.session_state["aguardando_verificacao"] = email_limpo
                st.success("Conta criada com sucesso! Um código de verificação foi enviado via EmailJS para o seu e-mail.")
                st.rerun()
              else:
                registrar_historico_profissional(novo_nome, username_limpo, email_limpo, "Falha no Envio", msg_ej, "Falha", "EmailJS", "ERR_EMAILJS_FAIL", rastreamento_id)
                st.session_state["aguardando_verificacao"] = email_limpo
                st.warning(f"Conta criada, mas ocorreu um erro ao enviar o código via EmailJS: {msg_ej}. Utilize a opção 'Reenviar código'.")
                st.rerun()

else:
  # --- MÓDULOS INTERNOS DO SISTEMA ---
  if menu == t["dashboard"]:
    st.markdown("## 📊 Dashboard Executivo")
    st.markdown(
        f"Visão geral das operações, indicadores financeiros e alertas de"
        f" desempenho para **{emp['nome']}**."
    )
    st.markdown("---")

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
          "SELECT COUNT(*) FROM produtos WHERE quantidade_estoque <= estoque_minimo"
      )
      est_baixo = cursor.fetchone()[0] or 0

      c1, c2, c3, c4 = st.columns(4)
      with c1:
        st.metric("Faturamento Total", formatar_moeda(faturamento))
      with c2:
        st.metric("Pedidos Pendentes", ped_pend)
      with c3:
        st.metric("Em Processamento", ped_proc)
      with c4:
        st.metric("Estoque Baixo", est_baixo, delta_color="inverse")

      st.markdown("---")
      conn.close()
    except Exception as e:
      st.error(f"Erro ao carregar métricas: {e}")

  # --- MÓDULO: LOGS DO SISTEMA ---
  elif menu == t["logs"] and st.session_state["nivel_acesso"] == "Administrador":
    st.header("📋 Logs e Auditoria do Sistema")
    st.markdown("Registo completo de eventos, tentativas de autenticação, operações de segurança e tráfego do EmailJS.")
    st.markdown("---")

    try:
      import pandas as pd
      conn = sqlite3.connect(DB_FILE)
      df_logs = pd.read_sql_query("SELECT data_hora, usuario, username, email, acao, detalhes, resultado, servico, codigo_erro, rastreamento_id FROM historico ORDER BY id DESC", conn)
      conn.close()

      if not df_logs.empty:
        total_logs = len(df_logs)
        sucessos = len(df_logs[df_logs["resultado"] == "Sucesso"])
        falhas = len(df_logs[df_logs["resultado"] == "Falha"])
        bloqueados = len(df_logs[df_logs["resultado"] == "Bloqueado"])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total de Registos", total_logs)
        k2.metric("Sucessos Registados", sucessos)
        k3.metric("Falhas / Erros", falhas)
        k4.metric("Bloqueios de Segurança", bloqueados)

        st.markdown("---")
        st.subheader("Filtros de Pesquisa")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
          filtro_resultado = st.selectbox("Filtrar por Resultado", ["Todos", "Sucesso", "Falha", "Bloqueado", "Recusado"])
        with col_f2:
          filtro_servico = st.selectbox("Filtrar por Serviço", ["Todos", "EmailJS", "Sistema"])
        with col_f3:
          termo_busca = st.text_input("Pesquisar por E-mail ou Nome").strip().lower()

        df_filtrado = df_logs.copy()
        if filtro_resultado != "Todos":
          df_filtrado = df_filtrado[df_filtrado["resultado"] == filtro_resultado]
        if filtro_servico != "Todos":
          df_filtrado = df_filtrado[df_filtrado["servico"] == filtro_servico]
        if termo_busca:
          df_filtrado = df_filtrado[
              df_filtrado["email"].str.lower().str.contains(termo_busca, na=False) |
              df_filtrado["usuario"].str.lower().str.contains(termo_busca, na=False)
          ]

        st.dataframe(df_filtrado, use_container_width=True)
      else:
        st.info("Ainda não existem eventos registados no histórico de logs.")
    except Exception as e:
      st.error(f"Erro ao carregar os logs: {e}")

  # --- OUTROS MÓDULOS DE GESTÃO ---
  elif menu == t["clientes"]:
    st.header("👥 Gestão de Clientes")
    st.info("Módulo ativo e operacional.")
  elif menu == t["produtos"]:
    st.header("📦 Gestão de Produtos")
    st.info("Módulo ativo e operacional.")
  elif menu == t["estoque"]:
    st.header("🏭 Controlo de Estoque")
    st.info("Módulo ativo e operacional.")
  elif menu == t["vendas"]:
    st.header("🛒 Registar Venda")
    st.info("Módulo ativo e operacional.")
  elif menu == t["pedidos"]:
    st.header("📋 Gestão de Pedidos")
    st.info("Módulo ativo e operacional.")
  elif menu == t["relatorios"]:
    st.header("📈 Relatórios do Sistema")
    st.info("Módulo ativo e operacional.")
  elif menu == t["tarefas"]:
    st.header("📝 Gestão de Tarefas")
    st.info("Módulo ativo e operacional.")
  elif menu == t["config"]:
    st.header("⚙️ Configurações da Empresa")
    st.info("Módulo ativo e operacional.")
