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

# --- CONFIGURAÇÃO DA BASE DE DADOS SQLITE ---
DB_FILE = "evolution_gestao.db"


def init_db():
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
                taxa_aplicada TEXT,
                data_hora TEXT
            )
        """)
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
  except Exception as e:
    st.error(f"Erro ao inicializar a base de dados: {e}")


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


# --- LISTA COMPLETA DE PAÍSES E MOEDAS ---
PAISES_MOEDAS = {
    "Afeganistão": {"moeda": "AFN", "simbolo": "؋", "idioma": "English", "fuso": "UTC+4:30"},
    "África do Sul": {"moeda": "ZAR", "simbolo": "R", "idioma": "English", "fuso": "UTC+2"},
    "Alemanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Deutsch", "fuso": "UTC+1"},
    "Angola": {"moeda": "AOA", "simbolo": "Kz", "idioma": "Português", "fuso": "UTC+1"},
    "Argentina": {"moeda": "ARS", "simbolo": "$", "idioma": "Español", "fuso": "UTC-3"},
    "Austrália": {"moeda": "AUD", "simbolo": "A$", "idioma": "English", "fuso": "UTC+10"},
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português", "fuso": "UTC-3"},
    "Canadá": {"moeda": "CAD", "simbolo": "CA$", "idioma": "English", "fuso": "UTC-5"},
    "China": {"moeda": "CNY", "simbolo": "¥", "idioma": "English", "fuso": "UTC+8"},
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español", "fuso": "UTC+1"},
    "Estados Unidos": {"moeda": "USD", "simbolo": "US$", "idioma": "English", "fuso": "UTC-5"},
    "França": {"moeda": "EUR", "simbolo": "€", "idioma": "Français", "fuso": "UTC+1"},
    "Japão": {"moeda": "JPY", "simbolo": "¥", "idioma": "English", "fuso": "UTC+9"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português", "fuso": "UTC+0"},
    "Reino Unido": {"moeda": "GBP", "simbolo": "£", "idioma": "English", "fuso": "UTC+0"},
}

# --- DICIONÁRIO MULTILÍNGUA ---
DICIONARIO = {
    "Deutsch": {
        "titulo": "🚀 A Evolution Online-Management",
        "menu": "Hauptmenü",
        "clientes": "Kundenverwaltung",
        "produtos": "Produktverwaltung",
        "vendas": "Verkauf",
        "dashboard": "Dashboard",
        "config": "Einstellungen",
        "ia": "KI-Assistent",
        "verificacao": "Sicherheit",
        "enviar_codigo": "Code senden",
        "email_label": "E-Mail",
        "codigo_label": "Code eingeben",
        "verificar": "Bestätigen",
        "sucesso_envio": "Gesendet!",
        "sucesso_verif": "Erfolgreich!",
        "erro_verif": "Fehler.",
        "add_cliente": "Kunden hinzufügen",
        "nome_cliente": "Name",
        "email_cliente": "E-Mail",
        "tel_cliente": "Telefon",
        "pais_cliente": "Land",
        "salvar": "Speichern",
        "lista_clientes": "Kundenliste",
        "add_produto": "Produkt hinzufügen",
        "nome_produto": "Produktname",
        "preco_produto": "Preis",
        "lista_produtos": "Produkte",
        "reg_venda": "Verkauf registrieren",
        "qtd": "Menge",
        "total_venda": "Gesamt",
        "historico_vendas": "Verlauf",
        "chat_ia": "Chat",
        "pergunta_ia": "Frage:",
        "enviar": "Senden",
        "sair": "Abmelden",
        "empresa_setup": "Unternehmensprofil",
    },
    "English": {
        "titulo": "🚀 A Evolution Online Management",
        "menu": "Main Menu",
        "clientes": "Client Management",
        "produtos": "Product Management",
        "vendas": "Sales & Invoicing",
        "dashboard": "Dashboard & Consolidated Reports",
        "config": "Regional Settings",
        "ia": "AI Assistant",
        "verificacao": "Security - Email Verification",
        "enviar_codigo": "Send Verification Code",
        "email_label": "Recipient Email Address",
        "codigo_label": "Enter received code (6 digits)",
        "verificar": "Validate and Sign In",
        "sucesso_envio": "Code successfully sent to the inbox!",
        "sucesso_verif": "Access granted successfully!",
        "erro_verif": "Incorrect code. Try again.",
        "add_cliente": "Register New Client",
        "nome_cliente": "Client Name",
        "email_cliente": "Email Address",
        "tel_cliente": "Phone Number",
        "pais_cliente": "Client Country",
        "salvar": "Save Changes",
        "lista_clientes": "Registered Clients Directory",
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
        "config": "Configuración Regional",
        "ia": "Asistente IA",
        "verificacao": "Seguridad",
        "enviar_codigo": "Enviar Código",
        "email_label": "Correo",
        "codigo_label": "Código",
        "verificar": "Verificar",
        "sucesso_envio": "¡Enviado!",
        "sucesso_verif": "¡Acceso autorizado!",
        "erro_verif": "Error.",
        "add_cliente": "Registrar Cliente",
        "nome_cliente": "Nombre",
        "email_cliente": "Correo",
        "tel_cliente": "Teléfono",
        "pais_cliente": "País",
        "salvar": "Guardar",
        "lista_clientes": "Clientes",
        "add_produto": "Añadir Producto",
        "nome_produto": "Nombre",
        "preco_produto": "Precio",
        "lista_produtos": "Productos",
        "reg_venda": "Registrar Venta",
        "qtd": "Cantidad",
        "total_venda": "Total",
        "historico_vendas": "Historial",
        "chat_ia": "IA",
        "pergunta_ia": "Pregunta:",
        "enviar": "Enviar",
        "sair": "Cerrar Sesión",
        "empresa_setup": "Perfil",
    },
    "Français": {
        "titulo": "🚀 A Evolution Gestion",
        "menu": "Menu Principal",
        "clientes": "Clients",
        "produtos": "Produits",
        "vendas": "Ventes",
        "dashboard": "Tableau de Bord",
        "config": "Paramètres",
        "ia": "Assistant IA",
        "verificacao": "Sécurité",
        "enviar_codigo": "Envoyer",
        "email_label": "E-mail",
        "codigo_label": "Code",
        "verificar": "Valider",
        "sucesso_envio": "Envoyé !",
        "sucesso_verif": "Succès !",
        "erro_verif": "Erreur.",
        "add_cliente": "Nouveau Client",
        "nome_cliente": "Nom",
        "email_cliente": "E-mail",
        "tel_cliente": "Téléphone",
        "pais_cliente": "Pays",
        "salvar": "Enregistrer",
        "lista_clientes": "Liste",
        "add_produto": "Nouveau Produit",
        "nome_produto": "Nom",
        "preco_produto": "Prix",
        "lista_produtos": "Stock",
        "reg_venda": "Vendre",
        "qtd": "Quantité",
        "total_venda": "Total",
        "historico_vendas": "Historique",
        "chat_ia": "Chat",
        "pergunta_ia": "Question:",
        "enviar": "Envoyer",
        "sair": "Déconnexion",
        "empresa_setup": "Profil",
    },
    "Português": {
        "titulo": "🚀 A Evolution Gestão Online",
        "menu": "Menu Principal",
        "clientes": "Gestão de Clientes",
        "produtos": "Gestão de Produtos",
        "vendas": "Vendas & Faturação",
        "dashboard": "Dashboard & Relatórios Consolidados",
        "config": "Configurações Regionais",
        "ia": "Assistente IA",
        "verificacao": "Segurança - Verificação de E-mail",
        "enviar_codigo": "Enviar Código de Verificação",
        "email_label": "Endereço de E-mail do Destinatário",
        "codigo_label": "Insira o código recebido (6 dígitos)",
        "verificar": "Validar e Entrar",
        "sucesso_envio": "Código enviado com sucesso para a caixa de entrada!",
        "sucesso_verif": "Acesso autorizado com sucesso!",
        "erro_verif": "Código incorreto. Tente novamente.",
        "add_cliente": "Registar Novo Cliente",
        "nome_cliente": "Nome do Cliente",
        "email_cliente": "Endereço de E-mail",
        "tel_cliente": "Número de Telefone",
        "pais_cliente": "País do Cliente",
        "salvar": "Guardar Alterações",
        "lista_clientes": "Diretório de Clientes Registados",
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

# --- CARREGAR DADOS GLOBAIS DA EMPRESA ---
emp = carregar_empresa()
simbolo_ativo = emp["simbolo"]
idioma_selecionado = emp["idioma"]

if idioma_selecionado not in DICIONARIO:
  idioma_selecionado = "Português"

t = DICIONARIO[idioma_selecionado]


# --- FUNÇÃO DE FORMATAÇÃO MONETÁRIA REATIVA ---
def formatar_moeda(valor, simbolo=simbolo_ativo):
  try:
    v = float(valor)
  except:
    v = 0.0
  if simbolo in ["R$", "$U", "ARS"]:
    return f"{simbolo} {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  else:
    return f"{simbolo} {v:,.2f}"


# --- FUNÇÃO DE CONVERSÃO CAMBIAL ---
def converter_cambio(valor, moeda_origem, moeda_destino):
  taxas = {"BRL": 1.0, "USD": 0.20, "EUR": 0.18, "GBP": 0.15, "JPY": 30.0}
  base_origem = taxas.get(moeda_origem, 1.0)
  base_destino = taxas.get(moeda_destino, 1.0)
  valor_em_brl = valor / base_origem
  convertido = valor_em_brl * base_destino
  ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  return convertido, ultima_atualizacao


# --- BARRA LATERAL ---
with st.sidebar:
  try:
    idiomas_ordenados = sorted(list(DICIONARIO.keys()))
    idioma_atual_idx = (
        idiomas_ordenados.index(idioma_selecionado)
        if idioma_selecionado in idiomas_ordenados
        else 0
    )
    idioma_sidebar = st.selectbox(
        "Idioma / Language", idiomas_ordenados, index=idioma_atual_idx
    )

    if idioma_sidebar != emp["idioma"]:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("UPDATE empresa SET idioma = ?", (idioma_sidebar,))
      conn.commit()
      conn.close()
      st.rerun()

    t = DICIONARIO[idioma_sidebar]

    if st.session_state["autenticado"]:
      st.markdown("---")
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
      st.info(f"📍 País: **{emp['pais']}**\n\n💱 Moeda: **{emp['moeda']} ({emp['simbolo']})**")
      st.markdown("---")
      if st.button(t["sair"]):
        st.session_state["autenticado"] = False
        st.session_state["codigo_enviado"] = ""
        st.rerun()
  except Exception as e:
    st.error(f"Erro na barra lateral: {e}")


# --- FUNÇÃO EMAILJS ---
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

# --- APLICAÇÃO PRINCIPAL ---
else:
  st.title(t["titulo"])

  if menu == t["clientes"]:
    st.header(t["clientes"])
    
    with st.form("form_cliente"):
      st.subheader(t["add_cliente"])
      nome_cli = st.text_input(t["nome_cliente"])
      email_cli = st.text_input(t["email_cliente"])
      tel_cli = st.text_input(t["tel_cliente"])
      
      paises_lista_completa = sorted(list(PAISES_MOEDAS.keys()))
      pais_cli = st.selectbox(t["pais_cliente"], paises_lista_completa)

      if st.form_submit_button(t["salvar"]):
        if nome_cli:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO clientes (nome, email, telefone, pais) VALUES (?,"
              " ?, ?, ?)",
              (nome_cli, email_cli, tel_cli, pais_cli),
          )
          conn.commit()
          conn.close()
          st.success(f"Cliente '{nome_cli}' registado com sucesso!")
          st.rerun()
        else:
          st.warning("O nome do cliente é obrigatório.")

    st.markdown("---")
    st.subheader(t["lista_clientes"])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, email, telefone, pais FROM clientes")
    clientes_db = cursor.fetchall()
    conn.close()

    for c in clientes_db:
      st.write(
          f"👤 **{c[0]}** | 📧 {c[1] or 'N/A'} | 📞 {c[2] or 'N/A'} | 🌍 País: {c[3]}"
      )

  elif menu == t["produtos"]:
    st.header(t["produtos"])
    
    with st.form("form_produto"):
      st.subheader(t["add_produto"])
      nome_prod = st.text_input(t["nome_produto"])
      preco_prod = st.number_input(
          f"{t['preco_produto']} ({simbolo_ativo})", min_value=0.0, format="%.2f"
      )

      if st.form_submit_button(t["salvar"]):
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
      valor_formatado = formatar_moeda(prod[1], simbolo_ativo)
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
                  "1.0",
                  data_hora,
              ),
          )
          conn.commit()
          conn.close()
          st.success("Venda registada com sucesso!")
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
      v_formatado = formatar_moeda(v[3], simbolo_ativo)
      st.write(
          f"📅 {v[5]} | **{v[0]}** comprou {v[2]}x *{v[1]}* — Total:"
          f" **{v_formatado}** ({emp['moeda']})"
      )

  elif menu == t["dashboard"]:
    st.header(t["dashboard"])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total) FROM vendas")
    res_soma = cursor.fetchone()[0]
    total_faturamento = res_soma if res_soma else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM vendas")
    total_transacoes = cursor.fetchone()[0]
    conn.close()

    col_a, col_b = st.columns(2)
    with col_a:
      st.metric("Total de Transações", total_transacoes)
    with col_b:
      st.metric(t["total_venda"], formatar_moeda(total_faturamento, simbolo_ativo))

    st.markdown("---")
    st.subheader("🌐 Relatório Consolidado Global")
    st.info(
        f"Operações ativas sob a jurisdição de **{emp['pais']}** | Moeda Padrão:"
        f" **{emp['moeda']} ({simbolo_ativo})**"
    )
    st.success(f"Faturamento Consolidado Global: **{formatar_moeda(total_faturamento, simbolo_ativo)}**")

  elif menu == t["config"]:
    st.header(t["config"])
    st.subheader(t["empresa_setup"])

    with st.form("form_empresa"):
      novo_nome_empresa = st.text_input("Nome da Empresa", value=emp["nome"])
      
      paises_lista_completa = sorted(list(PAISES_MOEDAS.keys()))
      pais_atual_idx = paises_lista_completa.index(emp["pais"]) if emp["pais"] in paises_lista_completa else 0
      
      novo_pais = st.selectbox("País de Operação", paises_lista_completa, index=pais_atual_idx)
      novo_pais_registro = st.selectbox(
          "País de Registo", paises_lista_completa, index=paises_lista_completa.index(emp["pais_registro"]) if emp["pais_registro"] in paises_lista_completa else 0
      )

      dados_pais = PAISES_MOEDAS.get(novo_pais, {"moeda": "USD", "simbolo": "US$", "idioma": "English", "fuso": "UTC"})
      nova_moeda = dados_pais["moeda"]
      novo_simbolo = dados_pais["simbolo"]
      sugestao_idioma = dados_pais["idioma"]

      col_m1, col_m2 = st.columns(2)
      with col_m1:
        moeda_input = st.text_input("Código da Moeda (ISO 4217)", value=nova_moeda)
      with col_m2:
        simbolo_input = st.text_input("Símbolo Monetário", value=novo_simbolo)

      st.info(f"💱 País Selecionado: **{novo_pais}** | Moeda Padrão: **{moeda_input} ({simbolo_input})** | Idioma Sugerido: **{sugestao_idioma}**")

      if st.form_submit_button(t["salvar"]):
        dados_atualizados = {
            "nome": novo_nome_empresa,
            "pais": novo_pais,
            "pais_registro": novo_pais_registro,
            "moeda": moeda_input,
            "simbolo": simbolo_input,
            "idioma": sugestao_idioma if sugestao_idioma in DICIONARIO else idioma_selecionado,
            "fuso": dados_pais["fuso"],
        }
        salvar_empresa_db(dados_atualizados)
        st.success("Configurações atualizadas globalmente!")
        st.rerun()

    st.markdown("---")
    st.subheader("💱 Conversor Cambial de Teste")
    val_conv = st.number_input("Valor a converter", min_value=0.0, value=100.0, format="%.2f")
    moeda_destino_teste = st.selectbox("Converter para", sorted(["BRL", "USD", "EUR", "GBP", "JPY"]))
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
            " recomendo manter o controlo fiscal alinhado com das taxas de câmbio correntes."
        )
      else:
        st.warning("Escreva uma pergunta.")
