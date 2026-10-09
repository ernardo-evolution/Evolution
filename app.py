from datetime import datetime
import os
import random
import sqlite3
import requests
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="A Evolution Gestão Online", page_icon="🚀", layout="wide"
)

# --- CREDENCIAIS EMAILJS ---
EMAILJS_URL = "https://api.emailjs.com/api/v1.0/email/send"
SERVICE_ID = "service_15qkad9"
TEMPLATE_ID = "template_mm4esan"
USER_ID = "PCUYqPfeqGQMvHbaD"
ACCESS_TOKEN = "Mt1w97IKOc8mG4pbR7AAU"

# --- CONFIGURAÇÃO DA BASE DE DADOS SQLITE (ESTRUTURA EXPANDIDA) ---
DB_FILE = "evolution_gestao.db"


def init_db():
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Empresa
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

    # Usuários e Permissões
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                nivel TEXT
            )
        """)

    # Clientes
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                telefone TEXT,
                pais TEXT
            )
        """)

    # Produtos e Estoque
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

    # Vendas
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

    # Pedidos com Fluxo Automatizado
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

    # Tarefas Integradas
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

    # Histórico de Atividades (Auditoria)
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

    # Inserir dados padrão da empresa apenas se vazio (sem utilizadores predefinidos)
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
  except Exception as e:
    st.error(f"Erro ao inicializar base de dados: {e}")


init_db()


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
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  cursor.execute(
      "INSERT INTO historico (usuario, acao, detalhes, data_hora) VALUES (?, ?,"
      " ?, ?)",
      (usuario, acao, detalhes, data_hora),
  )
  conn.commit()
  conn.close()


# --- LISTA DE PAÍSES E MOEDAS ---
PAISES_MOEDAS = {
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português"},
    "Estados Unidos": {"moeda": "USD", "simbolo": "US$", "idioma": "English"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português"},
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español"},
}

DICIONARIO = {
    "Português": {
        "titulo": "🚀 A Evolution Gestão Online",
        "menu": "Menu Principal",
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
}
t = DICIONARIO["Português"]

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
    st.warning("Efetue login para aceder ao sistema.")


# --- TELA DE LOGIN / REGISTO DE UTILIZADORES ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])
  tab_login, tab_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Registar Utilizador"])

  with tab_login:
    st.markdown("### Acesso Restrito ao Sistema")
    email_login = st.text_input("E-mail corporativo", key="login_email")
    if st.button("Entrar no Sistema"):
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
          st.success("Acesso autorizado com sucesso!")
          st.rerun()
        else:
          st.error(
              "Utilizador não encontrado. Registe-se na aba ao lado se ainda"
              " não tiver conta."
          )
      else:
        st.warning("Insira o seu e-mail.")

  with tab_registo:
    st.markdown("### Criar Nova Conta de Utilizador")
    with st.form("form_reg_novo_user"):
      nome_novo = st.text_input("Nome Completo")
      email_novo = st.text_input("E-mail Corporativo")
      nivel_novo = st.selectbox(
          "Nível de Acesso", ["Administrador", "Gerente", "Funcionário"]
      )
      if st.form_submit_button("Criar Conta"):
        if nome_novo and email_novo:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id FROM usuarios WHERE email = ?", (email_novo,)
          )
          existe = cursor.fetchone()
          if existe:
            st.error("Este e-mail já está registado.")
          else:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, nivel) VALUES (?, ?, ?)",
                (nome_novo, email_novo, nivel_novo),
            )
            conn.commit()
            conn.close()
            st.success("Conta criada com sucesso! Já pode fazer login.")
        else:
          st.warning("Preencha todos os campos obrigatórios.")

else:
  st.title(t["titulo"])

  # ==========================================
  # 1. DASHBOARD INTELIGENTE
  # ==========================================
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

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status_envio = 'Enviado'")
    ped_env = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM produtos WHERE quantidade_estoque <= estoque_minimo"
    )
    est_baixo = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status != 'Concluída'")
    tar_pend = cursor.fetchone()[0] or 0
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento Total", formatar_moeda(faturamento))
    c2.metric("Pedidos Pendentes", ped_pend)
    c3.metric("Em Processamento", ped_proc)
    c4.metric("Estoque Baixo (Alertas)", est_baixo, delta_color="inverse")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
      st.subheader("📋 Atividades Recentes do Sistema")
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT usuario, acao, detalhes, data_hora FROM historico ORDER BY id"
          " DESC LIMIT 5"
      )
      hist = cursor.fetchall()
      conn.close()
      for h in hist:
        st.write(f"🕒 {h[3]} | **{h[0]}**: {h[1]} ({h[2]})")

    with col_b:
      st.subheader("📌 Tarefas Prioritárias")
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT titulo, responsavel, prazo, prioridade FROM tarefas WHERE"
          " status != 'Concluída' LIMIT 5"
      )
      tarefas_dash = cursor.fetchall()
      conn.close()
      for td in tarefas_dash:
        st.warning(
            f"**{td[0]}** (Resp: {td[1]} | Prazo: {td[2]} | Prioridade:"
            f" {td[3]})"
        )

  # ==========================================
  # 2. CLIENTES
  # ==========================================
  elif menu == t["clientes"]:
    st.header("👥 Gestão de Clientes")
    with st.form("form_cli"):
      nome = st.text_input("Nome do Cliente")
      email = st.text_input("E-mail")
      tel = st.text_input("Telefone")
      pais = st.selectbox("País", list(PAISES_MOEDAS.keys()))
      if st.form_submit_button("Registar Cliente"):
        if nome:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO clientes (nome, email, telefone, pais) VALUES (?,"
              " ?, ?, ?)",
              (nome, email, tel, pais),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Registo de Cliente",
              f"Cliente {nome} adicionado",
          )
          st.success("Cliente registado!")
          st.rerun()

    st.subheader("Diretório de Clientes")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, email, telefone, pais FROM clientes")
    for c in cursor.fetchall():
      st.write(f"👤 **{c[0]}** | 📧 {c[1]} | 📞 {c[2]} | 🌍 {c[3]}")
    conn.close()

  # ==========================================
  # 3. PRODUTOS & 4. ESTOQUE
  # ==========================================
  elif menu == t["produtos"]:
    st.header("📦 Gestão de Produtos e Catálogo")
    with st.form("form_prod"):
      nome = st.text_input("Nome do Produto")
      preco = st.number_input("Preço Unitário", min_value=0.0, format="%.2f")
      qtd = st.number_input(
          "Quantidade Inicial em Estoque", min_value=0, step=1
      )
      est_min = st.number_input("Estoque Mínimo de Alerta", min_value=0, value=5)
      if st.form_submit_button("Guardar Produto"):
        if nome:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO produtos (nome, preco, quantidade_estoque,"
              " estoque_minimo, moeda, simbolo) VALUES (?, ?, ?, ?, ?, ?)",
              (
                  nome,
                  preco,
                  qtd,
                  est_min,
                  emp["moeda"],
                  simbolo_ativo,
              ),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Novo Produto",
              f"Produto {nome} cadastrado",
          )
          st.success("Produto cadastrado com sucesso!")
          st.rerun()

  elif menu == t["estoque"]:
    st.header("🏭 Controlo e Alertas de Estoque")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, quantidade_estoque, estoque_minimo FROM produtos"
    )
    prods = cursor.fetchall()
    conn.close()

    for p in prods:
      status_estoque = (
          "⚠️ Estoque Baixo"
          if p[2] <= p[3]
          else "✅ Nível Adequado"
      )
      st.write(
          f"📦 **{p[1]}** — Quantidade: **{p[2]}** un (Mínimo: {p[3]}) —"
          f" {status_estoque}"
      )

  # ==========================================
  # 5. VENDAS E AUTOMAÇÃO DE PEDIDOS
  # ==========================================
  elif menu == t["vendas"]:
    st.header("🛒 Registo de Vendas e Automação de Processos")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes")
    clientes = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT nome, preco, quantidade_estoque FROM produtos")
    produtos = cursor.fetchall()
    conn.close()

    if not clientes or not produtos:
      st.warning("Cadastre clientes e produtos antes de efetuar vendas.")
    else:
      with st.form("form_venda"):
        cli = st.selectbox("Cliente", clientes)
        prod_info = st.selectbox("Produto", [p[0] for p in produtos])
        qtd_venda = st.number_input(
            "Quantidade", min_value=1, value=1, step=1
        )

        if st.form_submit_button("Registar Venda (Disparar Automações)"):
          preco_u = 0
          estoque_atual = 0
          for p in produtos:
            if p[0] == prod_info:
              preco_u = p[1]
              estoque_atual = p[2]

          if qtd_venda > estoque_atual:
            st.error("Erro: Quantidade superior ao estoque disponível!")
          else:
            total = preco_u * qtd_venda
            data_h = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # 1. Registar Venda
            cursor.execute(
                "INSERT INTO vendas (cliente, produto, quantidade,"
                " valor_unitario, valor_total, moeda_original, data_hora)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cli, prod_info, qtd_venda, preco_u, total, emp["moeda"], data_h),
            )

            # 2. Atualizar Estoque Automaticamente
            novo_est = estoque_atual - qtd_venda
            cursor.execute(
                "UPDATE produtos SET quantidade_estoque = ? WHERE nome = ?",
                (novo_est, prod_info),
            )

            # 3. Criar Pedido Automático
            cursor.execute(
                "INSERT INTO pedidos (cliente, produto, quantidade,"
                " status_venda, status_separacao, status_envio, status_pedido,"
                " data_criacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cli,
                    prod_info,
                    qtd_venda,
                    "Concluída",
                    "Pendente",
                    "Aguardando",
                    "Em processamento",
                    data_h,
                ),
            )

            # 4. Criar Tarefa Automática para a Separação
            cursor.execute(
                "INSERT INTO tarefas (titulo, responsavel, prazo, prioridade,"
                " status, relacionamento, data_criacao) VALUES (?, ?, ?, ?, ?,"
                " ?, ?)",
                (
                    f"Separar produto para {cli}",
                    "Equipa de Logística",
                    "24 horas",
                    "Alta",
                    "Pendente",
                    f"Pedido - {cli}",
                    data_h,
                ),
            )

            conn.commit()
            conn.close()

            registrar_historico(
                st.session_state["usuario_atual"],
                "Nova Venda & Automação",
                f"Venda registada para {cli}. Pedido e tarefa de separação"
                " gerados automaticamente.",
            )
            st.success(
                "Venda registada! O sistema avançou o fluxo e gerou a tarefa de"
                " separação automaticamente."
            )
            st.rerun()

  # ==========================================
  # 6. PEDIDOS & 7. PRODUTOS ENVIADOS
  # ==========================================
  elif menu == t["pedidos"] or menu == t["enviados"]:
    st.header("📋 Gestão e Avanço Automático de Pedidos")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, cliente, produto, quantidade, status_venda,"
        " status_separacao, status_envio, status_pedido FROM pedidos"
    )
    peds = cursor.fetchall()
    conn.close()

    for p in peds:
      st.markdown(f"### Pedido #{p[0]} — Cliente: {p[1]}")
      st.write(
          f"📦 Produto: {p[2]} (Qtd: {p[3]}) | Venda: {p[4]} | Separação:"
          f" **{p[5]}** | Envio: **{p[6]}** | Status Geral: **{p[7]}**"
      )

      col_op1, col_op2 = st.columns(2)
      with col_op1:
        if p[5] == "Pendente" and st.button(
            f"Marcar como Separado #{p[0]}", key=f"sep_{p[0]}"
        ):
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE pedidos SET status_separacao = 'Concluído' WHERE id = ?",
              (p[0],),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Separação Concluída",
              f"Produto do pedido #{p[0]} separado.",
          )
          st.success("Status atualizado para Separado!")
          st.rerun()

      with col_op2:
        if p[5] == "Concluído" and p[6] != "Enviado" and st.button(
            f"Registar Envio #{p[0]}", key=f"env_{p[0]}"
        ):
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE pedidos SET status_envio = 'Enviado', status_pedido ="
              " 'Concluído' WHERE id = ?",
              (p[0],),
          )
          conn.commit()
          conn.close()
          registrar_historico(
              st.session_state["usuario_atual"],
              "Envio Registado",
              f"Pedido #{p[0]} enviado e concluído.",
          )
          st.success("Envio registado e pedido concluído com sucesso!")
          st.rerun()
      st.markdown("---")

  # ==========================================
  # 8. RELATÓRIOS
  # ==========================================
  elif menu == t["relatorios"]:
    st.header("📈 Relatórios Consolidados")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total) FROM vendas")
    f_total = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT COUNT(*) FROM vendas")
    n_vendas = cursor.fetchone()[0] or 0
    conn.close()

    st.success(f"Faturamento Consolidado: **{formatar_moeda(f_total)}**")
    st.info(f"Total de Transações Efetuadas: **{n_vendas}**")

  # ==========================================
  # 9. TAREFAS
  # ==========================================
  elif menu == t["tarefas"]:
    st.header("📝 Gestor Integrado de Tarefas")
    with st.form("form_tar"):
      tit = st.text_input("Título da Tarefa")
      resp = st.text_input(
          "Responsável", value=st.session_state["usuario_atual"]
      )
      prazo = st.text_input("Prazo (ex: 2 dias)")
      prio = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
      rel = st.text_input("Relacionamento (Cliente/Pedido)")
      if st.form_submit_button("Criar Tarefa"):
        if tit:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          data_h = datetime.now().strftime("%d/%m/%Y")
          cursor.execute(
              "INSERT INTO tarefas (titulo, responsavel, prazo, prioridade,"
              " status, relacionamento, data_criacao) VALUES (?, ?, ?, ?, ?, ?,"
              " ?)",
              (tit, resp, prazo, prio, "Pendente", rel, data_h),
          )
          conn.commit()
          conn.close()
          st.success("Tarefa criada com sucesso!")
          st.rerun()

    st.subheader("Lista de Tarefas Ativas")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, responsavel, prazo, prioridade, status FROM tarefas"
    )
    tarefas = cursor.fetchall()
    conn.close()

    for tr in tarefas:
      st.write(
          f"📌 **{tr[1]}** (Resp: {tr[2]} | Prazo: {tr[3]} | Prioridade:"
          f" {tr[4]} | Status: **{tr[5]}**)"
      )
      if tr[5] != "Concluída" and st.button(
          f"Concluir Tarefa #{tr[0]}", key=f"t_{tr[0]}"
      ):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tarefas SET status = 'Concluída' WHERE id = ?", (tr[0],)
        )
        conn.commit()
        conn.close()
        st.success("Tarefa concluída!")
        st.rerun()

  # ==========================================
  # 10. MYA (ASSISTENTE INTELIGENTE)
  # ==========================================
  elif menu == t["mya"]:
    st.header("🤖 MyA — Assistente Inteligente do Evolution")
    st.write(
        "Faça perguntas diretas sobre os processos, pedidos ou estado do"
        " sistema:"
    )

    pergunta = st.text_input(
        "Ex: 'O que falta para concluir o pedido do cliente X?' ou 'Tem algum"
        " pedido parado?'"
    )
    if st.button("Perguntar à MyA"):
      if pergunta:
        p_lower = pergunta.lower()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        resposta_mya = ""
        if "parado" in p_lower or "aguardando" in p_lower:
          cursor.execute(
              "SELECT COUNT(*) FROM pedidos WHERE status_separacao = 'Pendente'"
          )
          qtd_p = cursor.fetchone()[0]
          resposta_mya = (
              f"Existem {qtd_p} pedidos aguardando o processo de separação de"
              " produtos."
          )
        elif "pedido" in p_lower:
          cursor.execute(
              "SELECT id, cliente, status_separacao, status_envio FROM pedidos"
          )
          p_all = cursor.fetchall()
          detalhes_p = [
              f"Pedido #{p[0]} (Cliente: {p[1]} | Separação: {p[2]} | Envio:"
              f" {p[3]})"
              for p in p_all
          ]
          resposta_mya = (
              "Estado atual dos pedidos no sistema:\n- "
              + "\n- ".join(detalhes_p)
              if detalhes_p
              else "Não há pedidos registados."
          )
        else:
          cursor.execute("SELECT COUNT(*) FROM vendas")
          tot_v = cursor.fetchone()[0]
          resposta_mya = (
              f"Com base nas informações do sistema, temos {tot_v} vendas"
              " registadas e os fluxos estão operacionais."
          )

        conn.close()
        st.info(f"💡 **MyA:** {resposta_mya}")
      else:
        st.warning("Escreva uma pergunta.")

  # ==========================================
  # 11. CONFIGURAÇÕES
  # ==========================================
  elif menu == t["config"]:
    st.header(t["config"])
    with st.form("form_emp"):
      nome_emp = st.text_input("Nome da Empresa", value=emp["nome"])
      pais_op = st.selectbox(
          "País de Operação",
          list(PAISES_MOEDAS.keys()),
          index=list(PAISES_MOEDAS.keys()).index(emp["pais"])
          if emp["pais"] in PAISES_MOEDAS
          else 0,
      )
      if st.form_submit_button("Guardar Configurações"):
        dados_p = PAISES_MOEDAS[pais_op]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empresa")
        cursor.execute(
            "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo,"
            " idioma, fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                nome_emp,
                pais_op,
                pais_op,
                dados_p["moeda"],
                dados_p["simbolo"],
                dados_p["idioma"],
                "UTC-3",
            ),
        )
        conn.commit()
        conn.close()
        st.success("Configurações atualizadas!")
        st.rerun()
