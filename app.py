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

# --- DICIONÁRIO MULTILÍNGUA SIMPLIFICADO E SEGURO ---
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
        "config": "Configuración Regional y Pagos",
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
  taxas = {"BRL": 1.0, "USD": 0.20, "EUR": 0.1
