from datetime import datetime, timedelta
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

# --- 4. INICIALIZAÇÃO E MIGRAÇÃO DA BASE DE DADOS ---
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
            acao TEXT,
            detalhes TEXT,
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

  garantir_coluna("usuarios", "codigo_expiracao", "TEXT")
  garantir_coluna("usuarios", "tentativas_codigo", "INTEGER DEFAULT 0")
  garantir_coluna("produtos", "estoque_minimo", "INTEGER DEFAULT 4")
  garantir_coluna("empresa", "moeda", "TEXT")
  garantir_coluna("empresa", "simbolo", "TEXT")

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


# --- 5. FUNÇÕES AUXILIARES E EMAILJS ---
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


def disparar_emailjs(destinatario, nome_usuario, codigo):
  """Dispara o EmailJS de forma segura injetando script no cliente"""
  try:
    ej_conf = st.secrets.get("emailjs", {})
  except:
    ej_conf = {}

  service_id = ej_conf.get("service_id", "")
  template_id = ej_conf.get("template_id", "")
  public_key = ej_conf.get("public_key", "")

  if not service_id or not template_id or not public_key:
    return False

  html_code = f"""
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
    <script type="text/javascript">
       (function(){{
          emailjs.init("{public_key}");
       }})();
       
       var templateParams = {{
          to_email: "{destinatario}",
          to_name: "{nome_usuario}",
          message: "{codigo}",
          code: "{codigo}"
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
  return True


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
  except Exception as e:
    print(f"Erro ao registar histórico: {e}")


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
    st.warning(
        "🔒 Conta pendente de ativação. Um código de 6 dígitos foi enviado via EmailJS para o"
        f" seu e-mail: **{email_pendente}** (Validade: 10 minutos)"
    )
    
    with st.form("form_verificar_codigo"):
      codigo_inserido = st.text_input("Introduza o Código de Verificação (6 dígitos)", max_chars=6)
      col_btn1, col_btn2 = st.columns(2)
      with col_btn1:
        btn_confirmar = st.form_submit_button("Confirmar e Ativar Conta", use_container_width=True)
      with col_btn2:
        btn_reenviar = st.form_submit_button("Reenviar Código", use_container_width=True)

      if btn_confirmar:
        if not codigo_inserido.strip():
          st.error("Insira o código de verificação.")
        else:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id, nome, codigo_verificacao, codigo_expiracao, tentativas_codigo FROM usuarios WHERE email = ?",
              (email_pendente,),
          )
          user_row = cursor.fetchone()

          if not user_row:
            conn.close()
            st.error("Registo não encontrado.")
          else:
            u_id, u_nome, db_code, db_expiry, tentativas = user_row
            
            if tentativas >= 5:
              conn.close()
              st.error("Limite máximo de tentativas excedido (5/5). Solicite um novo registo.")
            else:
              exp_dt = datetime.strptime(db_expiry, "%Y-%m-%d %H:%M:%S") if db_expiry else datetime.min
              if datetime.now() > exp_dt:
                conn.close()
                st.error("O código expirou. Clique em 'Reenviar Código'.")
              elif db_code != codigo_inserido.strip():
                novo_tentativas = tentativas + 1
                cursor.execute("UPDATE usuarios SET tentativas_codigo = ? WHERE id = ?", (novo_tentativas, u_id))
                conn.commit()
                conn.close()
                st.error(f"Código incorreto. Tentativa {novo_tentativas} de 5.")
              else:
                cursor.execute(
                    "UPDATE usuarios SET ativo = 1, codigo_verificacao = NULL, codigo_expiracao = NULL, tentativas_codigo = 0 WHERE id = ?",
                    (u_id,),
                )
                conn.commit()
                conn.close()
                registrar_historico(email_pendente, "Ativação de Conta", "E-mail verificado com sucesso via EmailJS.")
                st.success("Conta verificada e ativada com sucesso! Já pode fazer login.")
                st.session_state["aguardando_verificacao"] = None
                st.rerun()

      if btn_reenviar:
        novo_codigo = f"{random.randint(0, 999999):06d}"
        nova_expiracao = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome FROM usuarios WHERE email = ?", (email_pendente,)
        )
        r_nome = cursor.fetchone()
        nome_usr = r_nome[0] if r_nome else "Utilizador"

        cursor.execute(
            "UPDATE usuarios SET codigo_verificacao = ?, codigo_expiracao = ?, tentativas_codigo = 0 WHERE email = ?",
            (novo_codigo, nova_expiracao, email_pendente)
        )
        conn.commit()
        conn.close()

        disparar_emailjs(email_pendente, nome_usr, novo_codigo)
        st.success("Um novo código de verificação foi disparado via EmailJS.")

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
                st.session_state["aguardando_verificacao"] = email_login
                st.error("Esta conta ainda não foi ativada. Introduza o código enviado para o seu e-mail.")
                st.rerun()
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
              st.error("Utilizador não encontrado. Crie uma conta na aba ao lado.")
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
          if not novo_nome.strip() or not novo_email.strip():
            st.warning("Preencha todos os campos obrigatórios.")
          elif "@" not in novo_email or "." not in novo_email:
            st.error("Introduza um endereço de e-mail válido.")
          else:
            email_limpo = novo_email.strip().lower()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ativo FROM usuarios WHERE email = ?", (email_limpo,))
            existe = cursor.fetchone()
            
            if existe:
              if existe[1] == 1:
                st.error("Este e-mail já está registado e ativo. Utilize o login.")
              else:
                st.session_state["aguardando_verificacao"] = email_limpo
                st.warning("Este e-mail já está registado mas aguarda ativação. Redirecionando para validação do código.")
                st.rerun()
              conn.close()
            else:
              codigo_verif = f"{random.randint(0, 999999):06d}"
              expiracao_dt = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

              cursor.execute(
                  "INSERT INTO usuarios (nome, email, nivel, ativo, codigo_verificacao, codigo_expiracao, tentativas_codigo) VALUES (?, ?, ?, 0, ?, ?, 0)",
                  (
                      novo_nome.strip(),
                      email_limpo,
                      novo_nivel,
                      codigo_verif,
                      expiracao_dt,
                  ),
              )
              conn.commit()
              conn.close()

              disparar_emailjs(email_limpo, novo_nome.strip(), codigo_verif)
              st.session_state["aguardando_verificacao"] = email_limpo
              st.success("Registo efetuado com sucesso! O código foi disparado para o seu e-mail via EmailJS.")
              st.rerun()

else:
  # --- MÓDULO: DASHBOARD EXECUTIVO REFINADO ---
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

      col_f1, col_f2 = st.columns([2, 4])
      with col_f1:
        filtro_periodo = st.selectbox(
            "Período de Análise",
            ["Todos os Registos", "Últimos 30 Dias", "Últimos 7 Dias"],
        )

      st.markdown("### 📈 Tendência de Vendas")
      cursor.execute("SELECT data_hora, valor_total FROM vendas ORDER BY id ASC")
      vendas_raw = cursor.fetchall()

      if vendas_raw:
        import pandas as pd
        df_vendas = pd.DataFrame(vendas_raw, columns=["data", "valor"])
        try:
          df_vendas["data_dt"] = pd.to_datetime(df_vendas["data"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
          df_vendas = df_vendas.dropna(subset=["data_dt"])
          if filtro_periodo == "Últimos 7 Dias":
            limite = datetime.now() - timedelta(days=7)
            df_vendas = df_vendas[df_vendas["data_dt"] >= limite]
          elif filtro_periodo == "Últimos 30 Dias":
            limite = datetime.now() - timedelta(days=30)
            df_vendas = df_vendas[df_vendas["data_dt"] >= limite]

          if not df_vendas.empty:
            df_grouped = df_vendas.groupby(df_vendas["data_dt"].dt.date)["valor"].sum().reset_index()
            df_grouped.columns = ["Data", "Valor Total"]
            df_grouped = df_grouped.set_index("Data")
            st.line_chart(df_grouped)
          else:
            st.info("Nenhum registo de vendas encontrado para o período selecionado.")
        except Exception as ex_chart:
          st.info(f"A aguardar mais dados de transações para gerar o gráfico temporal. ({ex_chart})")
      else:
        st.info("Sem dados de vendas registados. Efetue vendas no módulo correspondente para gerar gráficos.")

      st.markdown("---")

      col_sec1, col_sec2 = st.columns(2)

      with col_sec1:
        st.markdown("### 🛒 Vendas Recentes")
        cursor.execute("SELECT cliente, produto, quantidade, valor_total, data_hora FROM vendas ORDER BY id DESC LIMIT 5")
        vendas_recentes = cursor.fetchall()
        if vendas_recentes:
          for vr in vendas_recentes:
            st.markdown(f"- **{vr[0]}** adquiriu {vr[2]}x *{vr[1]}* — **{formatar_moeda(vr[3])}** `[{vr[4]}]`")
        else:
          st.info("Nenhuma venda recente registada.")

        st.markdown("### ⚠️ Alertas de Estoque Baixo")
        cursor.execute("SELECT nome, quantidade_estoque, estoque_minimo FROM produtos WHERE quantidade_estoque <= estoque_minimo")
        produtos_criticos = cursor.fetchall()
        if produtos_criticos:
          for pc in produtos_criticos:
            st.markdown(f"- Produto **{pc[0]}** com stock crítico: **{pc[1]}** unidades (Mínimo: {pc[2]})")
        else:
          st.success("Todos os produtos estão com níveis de stock seguros.")

      with col_sec2:
        st.markdown("### 📋 Pedidos que Precisam de Atenção")
        cursor.execute("SELECT id, cliente, produto, status_pedido FROM pedidos WHERE status_pedido != 'Concluído' LIMIT 5")
        pedidos_atencao = cursor.fetchall()
        if pedidos_atencao:
          for pa in pedidos_atencao:
            st.markdown(f"- **Pedido #{pa[0]}** ({pa[1]}) - Produto: {pa[2]} | Estado: `{pa[3]}`")
        else:
          st.success("Não existem pedidos pendentes de atenção.")

        st.markdown("### 🕒 Atividades Recentes do Sistema")
        cursor.execute("SELECT usuario, acao, detalhes, data_hora FROM historico ORDER BY id DESC LIMIT 5")
        historico_recente = cursor.fetchall()
        if historico_recente:
          for hr in historico_recente:
            st.text(f"[{hr[3]}] {hr[0]} -> {hr[1]}: {hr[2]}")
        else:
          st.info("Sem atividade recente registada no histórico.")

      conn.close()
    except Exception as e:
      st.error(f"Erro ao carregar os dados do dashboard: {e}")

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
          try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, email, telefone, pais) VALUES (?, ?, ?, ?)",
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
          except Exception as e:
            st.error(f"Erro ao gravar cliente na base de dados: {e}")
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
      p_min = st.number_input("Estoque Mínimo", min_value=0, value=4)
      if st.form_submit_button("Guardar Produto"):
        if p_nome:
          try:
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
          except Exception as e:
            st.error(f"Erro ao gravar produto: {e}")
        else:
          st.warning("O nome do produto é obrigatório.")

    st.markdown("---")
    st.subheader("Catálogo de Produtos")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, nome, preco, quantidade_estoque, estoque_minimo FROM"
          " produtos"
      )
      produtos = cursor.fetchall()
      conn.close()
      if produtos:
        for pr in produtos:
          st.markdown(
              f"**ID:** {pr[0]} | **Produto:** {pr[1]} | **Preço:** {formatar_moeda(pr[2])} | **Estoque:** {pr[3]} (Mín: {pr[4]})"
          )
      else:
        st.info("Nenhum produto registado.")
    except Exception as e:
      st.error(f"Erro ao listar produtos: {e}")

  # --- MÓDULO: ESTOQUE (COM OPÇÃO DE ELIMINAR) ---
  elif menu == t["estoque"]:
    st.header("🏭 Controlo de Estoque")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, nome, quantidade_estoque, estoque_minimo FROM produtos"
      )
      prods = cursor.fetchall()
      conn.close()
      
      if prods:
        st.subheader("Estado Atual do Stock")
        for pr in prods:
          status_est = "⚠️ BAIXO" if pr[2] <= pr[3] else "✅ Normal"
          st.markdown(
              f"- **{pr[1]}** — Quantidade: **{pr[2]}** | Mínimo: {pr[3]} | Estado: {status_est}"
          )
        
        st.markdown("---")
        st.subheader("🗑️ Remover Produto do Stock")
        with st.form("form_apagar_produto"):
          prod_nomes = [p[1] for p in prods]
          prod_para_apagar = st.selectbox("Selecione o produto que deseja eliminar", prod_nomes)
          btn_apagar = st.form_submit_button("Eliminar Produto do Sistema")
          
          if btn_apagar:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE nome = ?", (prod_para_apagar,))
            conn.commit()
            conn.close()
            registrar_historico(
                st.session_state["usuario_atual"],
                "Remover Produto",
                f"Produto {prod_para_apagar} eliminado do stock.",
            )
            st.success(f"Produto '{prod_para_apagar}' removido com sucesso!")
            st.rerun()
      else:
        st.info("Sem produtos no estoque.")
    except Exception as e:
      st.error(f"Erro ao consultar estoque: {e}")

  # --- MÓDULO: VENDAS ---
  elif menu == t["vendas"]:
    st.header("🛒 Registar Venda")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("SELECT nome FROM clientes")
      cli_list = [c[0] for c in cursor.fetchall()]
      cursor.execute(
          "SELECT nome, preco, quantidade_estoque FROM produtos WHERE"
          " quantidade_estoque > 0"
      )
      prod_data = cursor.fetchall()
      conn.close()

      if not cli_list:
        st.warning("⚠️ Não existem clientes registados. Adicione clientes primeiro no menu 'Clientes'.")
      elif not prod_data:
        st.warning("⚠️ Não existem produtos com estoque disponível para venda. Adicione produtos ou reponha o estoque.")
      else:
        prod_dict = {p[0]: {"preco": p[1], "estoque": p[2]} for p in prod_data}
        with st.form("form_registar_venda"):
          cli_sel = st.selectbox("Cliente", cli_list)
          prod_sel = st.selectbox("Produto", list(prod_dict.keys()))
          qtd_venda = st.number_input("Quantidade", min_value=1, value=1)
          btn_vender = st.form_submit_button("Concluir Venda")

          if btn_vender:
            preco_unit = prod_dict[prod_sel]["preco"]
            estoque_atual = prod_dict[prod_sel]["estoque"]
            if qtd_venda > estoque_atual:
              st.error("Quantidade superior ao estoque disponível!")
            else:
              val_total = qtd_venda * preco_unit
              data_h = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

              conn = sqlite3.connect(DB_FILE)
              cursor = conn.cursor()
              cursor.execute(
                  "INSERT INTO vendas (cliente, produto, quantidade,"
                  " valor_unitario, valor_total, moeda_original, data_hora)"
                  " VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (
                      cli_sel,
                      prod_sel,
                      qtd_venda,
                      preco_unit,
                      val_total,
                      emp["moeda"],
                      data_h,
                  ),
              )
              cursor.execute(
                  "UPDATE produtos SET quantidade_estoque = quantidade_estoque -"
                  " ? WHERE nome = ?",
                  (qtd_venda, prod_sel),
              )
              conn.commit()
              conn.close()

              registrar_historico(
                  st.session_state["usuario_atual"],
                  "Nova Venda",
                  f"Venda de {qtd_venda}x {prod_sel} para {cli_sel}.",
              )
              st.success("Venda efetuada com sucesso e estoque atualizado!")
              st.rerun()
    except Exception as e:
      st.error(f"Erro no módulo de vendas: {e}")

  # --- MÓDULO: PEDIDOS ---
  elif menu == t["pedidos"]:
    st.header("📋 Gestão de Pedidos")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, cliente, produto, quantidade, status_pedido FROM pedidos"
      )
      pedidos = cursor.fetchall()
      conn.close()
      if pedidos:
        for p in pedidos:
          st.markdown(
              f"**Pedido #{p[0]}** | Cliente: {p[1]} | Produto: {p[2]} | Qtd:"
              f" {p[3]} | Estado: **{p[4]}**"
          )
      else:
        st.info("Nenhum pedido registado.")
    except Exception as e:
      st.error(f"Erro ao carregar pedidos: {e}")

  # --- MÓDULO: RELATÓRIOS ---
  elif menu == t["relatorios"]:
    st.header("📈 Relatórios do Sistema")
    st.markdown(
        "Aqui pode visualizar o histórico de ações e relatórios financeiros."
    )
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("SELECT usuario, acao, detalhes, data_hora FROM historico")
      hist = cursor.fetchall()
      conn.close()
      if hist:
        for h in hist:
          st.text(f"[{h[3]}] {h[0]} - {h[1]}: {h[2]}")
      else:
        st.info("Sem registos no histórico.")
    except Exception as e:
      st.error(f"Erro ao carregar relatórios: {e}")

  # --- MÓDULO: TAREFAS ---
  elif menu == t["tarefas"]:
    st.header("📝 Gestão de Tarefas")
    with st.form("form_tarefa"):
      t_titulo = st.text_input("Título da Tarefa")
      t_resp = st.text_input("Responsável")
      t_prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
      if st.form_submit_button("Criar Tarefa"):
        if t_titulo:
          try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tarefas (titulo, responsavel, prioridade, status,"
                " data_criacao) VALUES (?, ?, ?, ?, ?)",
                (
                    t_titulo,
                    t_resp,
                    t_prioridade,
                    "Pendente",
                    datetime.now().strftime("%d/%m/%Y"),
                ),
            )
            conn.commit()
            conn.close()
            st.success("Tarefa criada!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao criar tarefa: {e}")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT titulo, responsavel, prioridade, status FROM tarefas"
      )
      tarefas = cursor.fetchall()
      conn.close()
      if tarefas:
        for tf in tarefas:
          st.markdown(
              f"**{tf[0]}** | Resp: {tf[1]} | Prioridade: {tf[2]} | Estado:"
              f" {tf[3]}"
          )
    except Exception as e:
      st.error(f"Erro ao listar tarefas: {e}")

  # --- MÓDULO: CONFIGURAÇÕES ---
  elif menu == t["config"]:
    st.header("⚙️ Configurações da Empresa e Moeda")
    try:
      with st.form("form_config"):
        novo_nome_emp = st.text_input("Nome da Empresa", value=emp.get("nome", "Evolution Corp Brasil"))

        paises_disponiveis = list(PAISES_MOEDAS.keys())
        pais_atual = emp.get("pais", "Brasil")
        idx_pais = (
            paises_disponiveis.index(pais_atual)
            if pais_atual in paises_disponiveis
            else 0
        )

        novo_pais = st.selectbox(
            "País da Empresa", paises_disponiveis, index=idx_pais
        )

        moeda_preview = PAISES_MOEDAS[novo_pais]["moeda"]
        simbolo_preview = PAISES_MOEDAS[novo_pais]["simbolo"]
        st.info(
            f"Moeda associada ao país escolhido: **{moeda_preview}**"
            f" ({simbolo_preview})"
        )

        if st.form_submit_button("Atualizar Configurações"):
          info_selecionada = PAISES_MOEDAS[novo_pais]
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE empresa SET nome = ?, pais = ?, moeda = ?, simbolo = ? WHERE"
              " id = 1",
              (
                  novo_nome_emp,
                  novo_pais,
                  info_selecionada["moeda"],
                  info_selecionada["simbolo"],
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              "Configurações atualizadas com sucesso! Símbolo alterado para"
              f" {info_selecionada['simbolo']}."
          )
          st.rerun()
    except Exception as e:
      st.error(f"Erro ao carregar as configurações: {e}")
