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

# --- CONFIGURAÇÃO DA BASE DE DADOS SQLITE (PERSISTÊNCIA REAL) ---
DB_FILE = "evolution_gestao.db"


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  # Tabela Empresa
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
  # Tabela Clientes
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
  # Tabela Produtos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco REAL,
            moeda TEXT,
            simbolo TEXT
        )
    """)
  # Tabela Vendas (com preservação histórica e câmbio)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            valor_total REAL,
            moeda_original TEXT,
            taxa_aplicada REAL,
            data_hora TEXT
        )
    """)
  conn.commit()
  
  # Inserir empresa padrão se a tabela estiver vazia
  cursor.execute("SELECT COUNT(*) FROM empresa")
  if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo, idioma,"
        " fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
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


init_db()


def carregar_empresa():
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
  return {
      "nome": "Evolution Corp Brasil",
      "pais": "Brasil",
      "pais_registro": "Brasil",
      "moeda": "BRL",
      "simbolo": "R$",
      "idioma": "Português",
      "fuso": "UTC-3",
  }


def salvar_empresa_db(dados):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM empresa")
  cursor.execute(
      "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo, idioma,"
      " fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
      (
          dados["nome"],
          dados["pais"],
          dados["pais_registro"],
          dados["moeda"],
          dados["simbolo"],
          dados["idioma"],
          dados["fuso"],
      ),
  )
  conn.commit()
  conn.close()


# --- BASE INTERNACIONAL DE PAÍSES E MOEDAS (ALFABÉTICA) ---
PAISES_MOEDAS = {
    "África do Sul": {"codigo": "ZA", "moeda": "ZAR", "simbolo": "ZAR", "idioma": "English", "fuso": "UTC+2"},
    "Angola": {"codigo": "AO", "moeda": "AOA", "simbolo": "Kz", "idioma": "Português", "fuso": "UTC+1"},
    "Argentina": {"codigo": "AR", "moeda": "ARS", "simbolo": "ARS", "idioma": "Español", "fuso": "UTC-3"},
    "Austrália": {"codigo": "AU", "moeda": "AUD", "simbolo": "A$", "idioma": "English", "fuso": "UTC+10"},
    "Brasil": {"codigo": "BR", "moeda": "BRL", "simbolo": "R$", "idioma": "Português", "fuso": "UTC-3"},
    "Cabo Verde": {"codigo": "CV", "moeda": "CVE", "simbolo": "CVE", "idioma": "Português", "fuso": "UTC-1"},
    "Canadá": {"codigo": "CA", "moeda": "CAD", "simbolo": "CA$", "idioma": "English", "fuso": "UTC-5"},
    "China": {"codigo": "CN", "moeda": "CNY", "simbolo": "CN¥", "idioma": "English", "fuso": "UTC+8"},
    "Espanha": {"codigo": "ES", "moeda": "EUR", "simbolo": "€", "idioma": "Español", "fuso": "UTC+1"},
    "Estados Unidos": {"codigo": "US", "moeda": "USD", "simbolo": "US$", "idioma": "English", "fuso": "UTC-5"},
    "Índia": {"codigo": "IN", "moeda": "INR", "simbolo": "₹", "idioma": "English", "fuso": "UTC+5:30"},
    "Japão": {"codigo": "JP", "moeda": "JPY", "simbolo": "¥", "idioma": "English", "fuso": "UTC+9"},
    "México": {"codigo": "MX", "moeda": "MXN", "simbolo": "MX$", "idioma": "Español", "fuso": "UTC-6"},
    "Moçambique": {"codigo": "MZ", "moeda": "MZN", "simbolo": "MT", "idioma": "Português", "fuso": "UTC+2"},
    "Paraguai": {"codigo": "PY", "moeda": "PYG", "simbolo": "₲", "idioma": "Español", "fuso": "UTC-4"},
    "Portugal": {"codigo": "PT", "moeda": "EUR", "simbolo": "€", "idioma": "Português", "fuso": "UTC+0"},
    "Reino Unido": {"codigo": "GB", "moeda": "GBP", "simbolo": "£", "idioma": "English", "fuso": "UTC+0"},
    "Suíça": {"codigo": "CH", "moeda": "CHF", "simbolo": "CHF", "idioma": "English", "fuso": "UTC+1"},
    "Uruguai": {"codigo": "UY", "moeda": "UYU", "simbolo": "$U", "idioma": "Español", "fuso": "UTC-3"},
}

# --- DICIONÁRIO MULTILÍNGUA COM ITENS EM ORDEM ALFABÉTICA ---
DICIONARIO = {
    "English": {
        "titulo": "🚀 A Evolution Online Management",
        "menu": "Main Menu",
        "clientes": "Client Management",
        "produtos": "Product Management",
        "vendas": "Sales & Invoicing",
        "dashboard": "Dashboard & Consolidated Reports",
        "config": "Regional Settings & Payments",
        "ia": "AI Assistant",
        "verificacao": "Security - Email Verification",
        "enviar_codigo": "Send Verification Code",
        "email_label": "Recipient Email Address",
        "codigo_label": "Enter received code (6 digits)",
        "verificar": "Validate and Sign In",
        "sucesso_envio": "Code successfully sent to the inbox!",
        "sucesso_verif": "Access granted successfully!",
        "erro_verif": "Incorrect code. Try again.",
        "add_cliente": "Add New Client",
        "nome_cliente": "Client Name",
        "salvar": "Save Changes",
        "lista_clientes": "Registered Clients",
        "add_produto": "Add New Product",
        "nome_produto": "Product Name",
        "preco_produto": "Price",
        "lista_produtos": "Products in Stock",
        "reg_venda": "Register Sale",
        "qtd": "Quantity",
        "total_venda": "Total Sales",
        "historico_vendas": "Sales History",
        "chat_ia": "Chat with AI Assistant",
        "pergunta_ia": "Type your management question:",
        "enviar": "Send Question",
        "sair": "Sign Out",
        "empresa_setup": "Company Profile & Registration",
    },
    "Español": {
        "titulo": "🚀 A Evolution Gestión Online",
        "menu": "Menú Principal",
        "clientes": "Gestión de Clientes",
        "produtos": "Gestión de Productos",
        "vendas": "Ventas y Facturación",
        "dashboard": "Panel y Informes Consolidados",
        "config": "Configuración Regional y Pagos",
        "ia": "Asistente IA",
        "verificacao": "Segurança - Verificación de Correo",
        "enviar_codigo": "Enviar Código de Verificación",
        "email_label": "Correo Electrónico del Destinatario",
        "codigo_label": "Ingrese el código recibido (6 dígitos)",
        "verificar": "Validar y Entrar",
        "sucesso_envio": "¡Código enviado con éxito a la bandeja de entrada!",
        "sucesso_verif": "¡Acceso autorizado com éxito!",
        "erro_verif": "Código incorrecto. Inténtelo de nuevo.",
        "add_cliente": "Añadir Nuevo Cliente",
        "nome_cliente": "Nombre del Cliente",
        "salvar": "Guardar Cambios",
        "lista_clientes": "Clientes Registrados",
        "add_produto": "Añadir Nuevo Producto",
        "nome_produto": "Nombre del Producto",
        "preco_produto": "Precio",
        "lista_produtos": "Productos en Stock",
        "reg_venda": "Registrar Venta",
        "qtd": "Cantidad",
        "total_venda": "Ventas Totales",
        "historico_vendas": "Historial de Ventas",
        "chat_ia": "Chatea con el Asistente IA",
        "pergunta_ia": "Escribe tu duda de gestión:",
        "enviar": "Enviar Pregunta",
        "sair": "Cerrar Sesión",
        "empresa_setup": "Registro y Perfil de Empresa",
    },
    "Português": {
        "titulo": "🚀 A Evolution Gestão Online",
        "menu": "Menu Principal",
        "clientes": "Gestão de Clientes",
        "produtos": "Gestão de Produtos",
        "vendas": "Vendas & Faturação",
        "dashboard": "Dashboard & Relatórios Consolidados",
        "config": "Configurações Regionais & Pagamentos",
        "ia": "Assistente IA",
        "verificacao": "Segurança - Verificação de E-mail",
        "enviar_codigo": "Enviar Código de Verificação",
        "email_label": "Endereço de E-mail do Destinatário",
        "codigo_label": "Insira o código recebido (6 dígitos)",
        "verificar": "Validar e Entrar",
        "sucesso_envio": "Código enviado com sucesso para a caixa de entrada!",
        "sucesso_verif": "Acesso autorizado com sucesso!",
        "erro_verif": "Código incorreto. Tente novamente.",
        "add_cliente": "Adicionar Novo Cliente",
        "nome_cliente": "Nome do Cliente",
        "salvar": "Guardar Alterações",
        "lista_clientes": "Clientes Registados",
        "add_produto": "Adicionar Novo Produto",
        "nome_produto": "Nome do Produto",
        "preco_produto": "Preço",
        "lista_produtos": "Produtos em Stock",
        "reg_venda": "Registar Venda",
        "qtd": "Quantidade",
        "total_venda": "Vendas Totais",
        "historico_vendas": "Histórico de Vendas",
        "chat_ia": "Converse com o Assistente IA",
        "pergunta_ia": "Escreva a sua dúvida sobre gestão:",
        "enviar": "Enviar Pergunta",
        "sair": "Terminar Sessão",
        "empresa_setup": "Registo e Perfil da Empresa",
    },
}

# --- ESTADOS DA SESSÃO ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "codigo_enviado" not in st.session_state:
  st.session_state["codigo_enviado"] = ""

# --- FUNÇÃO DE FORMATAÇÃO MONETÁRIA SEGURA ---
def formatar_moeda(valor, simbolo="R$"):
  try:
    v = float(valor)
  except:
    v = 0.0
  if simbolo in ["R$", "$U", "ARS"]:
    return f"{simbolo} {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  else:
    return f"{simbolo} {v:,.2f}"


# --- FUNÇÃO DE CONVERSÃO CAMBIAL AUTOMÁTICA ---
def converter_cambio(valor, moeda_origem, moeda_destino):
  taxas = {
      "BRL": 1.0,
      "USD": 0.20,
      "EUR": 0.18,
      "GBP": 0.15,
      "JPY": 30.0,
      "AOA": 180.0,
      "MZN": 12.5,
  }
  base_origem = taxas.get(moeda_origem, 1.0)
  base_destino = taxas.get(moeda_destino, 1.0)
  valor_em_brl = valor / base_origem
  convertido = valor_em_brl * base_destino
  ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  return convertido, ultima_atualizacao


# --- SELETOR DE IDIOMA E NAVEGAÇÃO NA BARRA LATERAL (EM ORDEM ALFABÉTICA) ---
with st.sidebar:
  idiomas_ordenados = sorted(list(DICIONARIO.keys()))
  idioma_atual = st.selectbox("Idioma / Language", idiomas_ordenados)
  t = DICIONARIO[idioma_atual]

  if st.session_state["autenticado"]:
    st.markdown("---")
    
    # Lista de opções do menu principal em ordem alfabética estrita
    opcoes_nao_ordenadas = [
        t["ia"],
        t["clientes"],
        t["config"],
        t["dashboard"],
        t["produtos"],
        t["vendas"],
    ]
    opcoes_menu = sorted(opcoes_nao_ordenadas)

    menu = st.radio(t["menu"], opcoes_menu)
    st.markdown("---")
    if st.button(t["sair"]):
      st.session_state["autenticado"] = False
      st.session_state["codigo_enviado"] = ""
      st.rerun()


# --- FUNÇÃO DE ENVIO EMAILJS ---
def disparar_emailjs(email_destino, codigo):
  payload = {
      "service_id": SERVICE_ID,
      "template_id": TEMPLATE_ID,
      "user_id": USER_ID,
      "accessToken": ACCESS_TOKEN,
      "template_params": {
          "to_email": email_destino,
          "email": email_destino,
          "codigo": codigo,
      },
  }
  try:
    resposta = requests.post(EMAILJS_URL, json=payload)
    return resposta.status_code == 200
  except Exception:
    return False


# --- BLOCO DE SEGURANÇA / LOGIN ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])
  st.markdown("### Acesso Restrito - Validação por E-mail")

  col1, col2 = st.columns([1, 1], gap="large")

  with col1:
    st.markdown("#### Entrar no Sistema")
    email_input = st.text_input(t["email_label"])

    if st.button(t["enviar_codigo"], use_container_width=True):
      if email_input:
        novo_codigo = str(random.randint(100000, 999999))
        st.session_state["codigo_enviado"] = novo_codigo

        sucesso = disparar_emailjs(email_input, novo_codigo)
        if sucesso:
          st.success(t["sucesso_envio"])
        else:
          st.error("Erro ao comunicar com o EmailJS.")
      else:
        st.warning("Insira um e-mail válido.")

    if st.session_state["codigo_enviado"]:
      codigo_digitado = st.text_input(
          t["codigo_label"], type="password", max_chars=6
      )
      if st.button(t["verificar"], use_container_width=True):
        if codigo_digitado == st.session_state["codigo_enviado"]:
          st.session_state["autenticado"] = True
          st.success(t["sucesso_verif"])
          st.rerun()
        else:
          st.error(t["erro_verif"])

  with col2:
    st.image(
        "https://img.freepik.com/free-vector/business-team-brainstorming-discussing-startup-project_74855-6908.jpg",
        use_column_width=True,
    )

# --- APLICAÇÃO PRINCIPAL MULTINACIONAL (SÓ ABRE APÓS AUTENTICAÇÃO) ---
else:
  st.title(t["titulo"])
  emp = carregar_empresa()
  simbolo_ativo = emp["simbolo"]

  if menu == t["clientes"]:
    st.header(t["clientes"])
    nome_cli = st.text_input(t["nome_cliente"])
    if st.button(t["salvar"]):
      if nome_cli:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome) VALUES (?)", (nome_cli,))
        conn.commit()
        conn.close()
        st.success(f"Cliente '{nome_cli}' adicionado com sucesso!")
        st.rerun()
      else:
        st.warning("O nome não pode estar vazio.")

    st.subheader(t["lista_clientes"])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes")
    clientes_db = cursor.fetchall()
    conn.close()
    for cli in clientes_db:
      st.write(f"- {cli[0]}")

  elif menu == t["produtos"]:
    st.header(t["produtos"])
    nome_prod = st.text_input(t["nome_produto"])
    preco_prod = st.number_input(
        f"{t['preco_produto']} ({simbolo_ativo})", min_value=0.0, format="%.2f"
    )

    if st.button(t["salvar"]):
      if nome_prod:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, preco, moeda, simbolo) VALUES (?, ?,"
            " ?, ?)",
            (nome_prod, preco_prod, emp["moeda"], simbolo_ativo),
        )
        conn.commit()
        conn.close()
        st.success(f"Produto '{nome_prod}' adicionado com sucesso!")
        st.rerun()
      else:
        st.warning("Insira o nome do produto.")

    st.subheader(t["lista_produtos"])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, preco, simbolo FROM produtos")
    produtos_db = cursor.fetchall()
    conn.close()
    for prod in produtos_db:
      valor_formatado = formatar_moeda(prod[1], prod[2])
      st.write(f"- **{prod[0]}**: {valor_formatado}")

  elif menu == t["vendas"]:
    st.header(t["vendas"])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes")
    clientes_list = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT nome, preco FROM produtos")
    produtos_list = cursor.fetchall()
    conn.close()

    if not clientes_list or not produtos_list:
      st.warning("Cadastre pelo menos um cliente e um produto antes de efetuar vendas.")
    else:
      with st.form("form_venda"):
        cli_selecionado = st.selectbox("Cliente", clientes_list)
        prod_selecionado = st.selectbox(
            "Produto", [p[0] for p in produtos_list]
        )
        qtd = st.number_input(t["qtd"], min_value=1, value=1, step=1)
        
        # Obter preço unitário do produto selecionado
        preco_unit = 0.0
        for p in produtos_list:
          if p[0] == prod_selecionado:
            preco_unit = p[1]

        st.info(f"Preço Unitário: {formatar_moeda(preco_unit, simbolo_ativo)}")

        if st.form_submit_button(t["reg_venda"]):
          total = preco_unit * qtd
          data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
          
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO vendas (cliente, produto, quantidade,"
              " valor_unitario, valor_total, moeda_original, taxa_aplicada,"
              " data_hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  cli_selecionado,
                  prod_selecionado,
                  qtd,
                  preco_unit,
                  total,
                  emp["moeda"],
                  1.0,
                  data_hora,
              ),
          )
          conn.commit()
          conn.close()
          st.success("Venda registada com sucesso com preservação histórica!")
          st.rerun()

    st.markdown("---")
    st.subheader(t["historico_vendas"])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cliente, produto, quantidade, valor_total, moeda_original,"
        " data_hora FROM vendas ORDER BY id DESC"
    )
    vendas_db = cursor.fetchall()
    conn.close()

    for v in vendas_db:
      simb_venda = "R$" if v[4] == "BRL" else ("€" if v[4] == "EUR" else "US$" if v[4] == "USD" else v[4])
      v_formatado = formatar_moeda(v[3], simb_venda)
      st.write(
          f"📅 {v[5]} | **{v[0]}** comprou {v[2]}x *{v[1]}* — Total:"
          f" **{v_formatado}** ({v[4]})"
      )

  elif menu == t["dashboard"]:
    st.header(t["dashboard"])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total), moeda_original FROM vendas GROUP BY moeda_original")
    totais = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM vendas")
    total_transacoes = cursor.fetchone()[0]
    conn.close()

    col_a, col_b = st.columns(2)
    with col_a:
      st.metric("Total de Transações", total_transacoes)
    with col_b:
      faturamento_str = "Nenhum registo"
      if totais:
        faturamento_str = " | ".join([f"{formatar_moeda(t[0], 'R$' if t[1]=='BRL' else '€' if t[1]=='EUR' else 'US$')} ({t[1]})" for t in totais])
      st.metric(t["total_venda"], faturamento_str)

    st.markdown("---")
    st.subheader("🌐 Relatório Consolidado (Moeda-Base: BRL)")
    st.info(
        "As vendas realizadas em outras moedas são convertidas para a moeda-base"
        " consolidada respeitando o câmbio oficial da data."
    )
    
    # Exemplo de relatório consolidado simulado com base no banco
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT valor_total, moeda_original FROM vendas")
    todas_vendas = cursor.fetchall()
    conn.close()

    total_brl_consolidado = 0.0
    for v_val, v_moeda in todas_vendas:
      conv, _ = converter_cambio(v_val, v_moeda, "BRL")
      total_brl_consolidado += conv

    st.success(f"Faturamento Consolidado Global em BRL: **{formatar_moeda(total_brl_consolidado, 'R$')}**")

  elif menu == t["config"]:
    st.header(t["config"])
    st.subheader(t["empresa_setup"])

    with st.form("form_empresa"):
      novo_nome_empresa = st.text_input("Nome da Empresa", value=emp["nome"])
      
      paises_lista = sorted(list(PAISES_MOEDAS.keys()))
      pais_atual_idx = paises_lista.index(emp["pais"]) if emp["pais"] in paises_lista else 0
      
      novo_pais = st.selectbox("País de Operação", paises_lista, index=pais_atual_idx)
      novo_pais_registro = st.selectbox(
          "País de Registo", paises_lista, index=paises_lista.index(emp["pais_registro"]) if emp["pais_registro"] in paises_lista else 0
      )

      info_pais = PAISES_MOEDAS[novo_pais]
      nova_moeda = info_pais["moeda"]
      novo_simbolo = info_pais["simbolo"]
      novo_idioma = info_pais["idioma"]
      novo_fuso = info_pais["fuso"]

      st.info(f"💱 Moeda Oficial Associada: **{nova_moeda} ({novo_simbolo})** | Fuso: **{novo_fuso}**")

      if st.form_submit_button(t["salvar"]):
        dados_atualizados = {
            "nome": novo_nome_empresa,
            "pais": novo_pais,
            "pais_registro": novo_pais_registro,
            "moeda": nova_moeda,
            "simbolo": novo_simbolo,
            "idioma": novo_idioma,
            "fuso": novo_fuso,
        }
        salvar_empresa_db(dados_atualizados)
        st.success("Configurações regionais guardadas permanentemente na base de dados!")
        st.rerun()

    st.markdown("---")
    st.subheader("💳 Métodos de Pagamento Regionais")
    if emp["pais"] == "Brasil":
      st.write("🟢 **PIX** (Ativado - Ambiente de Produção/Teste)")
      st.write("🟢 **Boleto Bancário** (Ativado)")
      st.write("🔵 **Cartões Nacionais e Internacionais**")
    else:
      st.write("🟢 **PayPal Internacional**")
      st.write(f"🟢 **Transferência Bancária ({emp['moeda']})**")
      st.write("🟢 **Cartões de Crédito Internacionais (Visa/Mastercard)**")

    st.markdown("---")
    st.subheader("💱 Conversor Cambial de Teste & Verificação Financeira")
    val_conv = st.number_input("Valor a converter", min_value=0.0, value=100.0, format="%.2f")
    moeda_destino_teste = st.selectbox("Converter para", sorted(["BRL", "USD", "EUR", "GBP", "JPY", "AOA", "MZN"]))
    if st.button("Simular Conversão"):
      res_conv, data_hora = converter_cambio(val_conv, emp["moeda"], moeda_destino_teste)
      st.success(
          f"Valor Original: {formatar_moeda(val_conv, emp['simbolo'])} | Convertido ({moeda_destino_teste}): {formatar_moeda(res_conv, 'US$' if moeda_destino_teste=='USD' else '€' if moeda_destino_teste=='EUR' else 'R$')}"
          f"\n\n🕒 Última atualização cambial: {data_hora}"
      )

  elif menu == t["ia"]:
    st.header(t["chat_ia"])
    pergunta = st.text_input(t["pergunta_ia"])
    if st.button(t["enviar"]):
      if pergunta:
        st.info(
            f"💡 **IA Evolution:** Analisando a sua questão sobre gestão multi-moeda ('{pergunta}'),"
            f" com operações a partir de **{emp['pais']} ({emp['moeda']})**,"
            " recomendo manter o controlo fiscal alinhado com as taxas de câmbio correntes."
        )
      else:
        st.warning("Escreva uma pergunta.")
