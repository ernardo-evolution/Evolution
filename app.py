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


# --- LISTA COMPLETA INTERNACIONAL DE PAÍSES E MOEDAS (ALFABÉTICA) ---
PAISES_MOEDAS = {
    "Afeganistão": {"moeda": "AFN", "simbolo": "؋", "idioma": "العربية (Arabic)", "fuso": "UTC+4:30"},
    "África do Sul": {"moeda": "ZAR", "simbolo": "R", "idioma": "English", "fuso": "UTC+2"},
    "Albânia": {"moeda": "ALL", "simbolo": "L", "idioma": "English", "fuso": "UTC+1"},
    "Alemanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Deutsch (German)", "fuso": "UTC+1"},
    "Andorra": {"moeda": "EUR", "simbolo": "€", "idioma": "Español", "fuso": "UTC+1"},
    "Angola": {"moeda": "AOA", "simbolo": "Kz", "idioma": "Português", "fuso": "UTC+1"},
    "Arábia Saudita": {"moeda": "SAR", "simbolo": "﷼", "idioma": "العربية (Arabic)", "fuso": "UTC+3"},
    "Argentina": {"moeda": "ARS", "simbolo": "$", "idioma": "Español", "fuso": "UTC-3"},
    "Austrália": {"moeda": "AUD", "simbolo": "A$", "idioma": "English", "fuso": "UTC+10"},
    "Áustria": {"moeda": "EUR", "simbolo": "€", "idioma": "Deutsch (German)", "fuso": "UTC+1"},
    "Bélgica": {"moeda": "EUR", "simbolo": "€", "idioma": "Français (French)", "fuso": "UTC+1"},
    "Brasil": {"moeda": "BRL", "simbolo": "R$", "idioma": "Português", "fuso": "UTC-3"},
    "Canadá": {"moeda": "CAD", "simbolo": "CA$", "idioma": "English", "fuso": "UTC-5"},
    "Chile": {"moeda": "CLP", "simbolo": "$", "idioma": "Español", "fuso": "UTC-4"},
    "China": {"moeda": "CNY", "simbolo": "¥", "idioma": "中文 (Chinese)", "fuso": "UTC+8"},
    "Colômbia": {"moeda": "COP", "simbolo": "$", "idioma": "Español", "fuso": "UTC-5"},
    "Coreia do Sul": {"moeda": "KRW", "simbolo": "₩", "idioma": "English", "fuso": "UTC+9"},
    "Espanha": {"moeda": "EUR", "simbolo": "€", "idioma": "Español", "fuso": "UTC+1"},
    "Estados Unidos": {"moeda": "USD", "simbolo": "US$", "idioma": "English", "fuso": "UTC-5"},
    "França": {"moeda": "EUR", "simbolo": "€", "idioma": "Français (French)", "fuso": "UTC+1"},
    "Índia": {"moeda": "INR", "simbolo": "₹", "idioma": "English", "fuso": "UTC+5:30"},
    "Itália": {"moeda": "EUR", "simbolo": "€", "idioma": "English", "fuso": "UTC+1"},
    "Japão": {"moeda": "JPY", "simbolo": "¥", "idioma": "日本語 (Japanese)", "fuso": "UTC+9"},
    "México": {"moeda": "MXN", "simbolo": "Mex$", "idioma": "Español", "fuso": "UTC-6"},
    "Moçambique": {"moeda": "MZN", "simbolo": "MT", "idioma": "Português", "fuso": "UTC+2"},
    "Portugal": {"moeda": "EUR", "simbolo": "€", "idioma": "Português", "fuso": "UTC+0"},
    "Reino Unido": {"moeda": "GBP", "simbolo": "£", "idioma": "English", "fuso": "UTC+0"},
    "Rússia": {"moeda": "RUB", "simbolo": "₽", "idioma": "Русский (Russian)", "fuso": "UTC+3"},
    "Suíça": {"moeda": "CHF", "simbolo": "CHF", "idioma": "English", "fuso": "UTC+1"},
    "Uruguai": {"moeda": "UYU", "simbolo": "$U", "idioma": "Español", "fuso": "UTC-3"},
}

# --- DICIONÁRIO MULTILÍNGUA COMPLETO ---
DICIONARIO = {
    "العربية (Arabic)": {
        "titulo": "🚀 إيفولوشن لإدارة الأعمال عبر الإنترنت",
        "menu": "القائمة الرئيسية",
        "clientes": "إدارة العملاء",
        "produtos": "إدارة المنتجات",
        "vendas": "المبيعات والفوترة",
        "dashboard": "لوحة التحكّم والتقارير الموحدة",
        "config": "الإعدادات الإقليمية والمدفوعات",
        "ia": "مساعد الذكاء الاصطناعي",
        "verificacao": "الأمان - التحقق من البريد الإلكتروني",
        "enviar_codigo": "إرسال رمز التحقق",
        "email_label": "البريد الإلكتروني للمستلم",
        "codigo_label": "أدخل الرمز المستلم (6 أرقام)",
        "verificar": "تحقق وتسجيل الدخول",
        "sucesso_envio": "تم إرسال الرمز بنجاح إلى البريد!",
        "sucesso_verif": "تم منح الوصول بنجاح!",
        "erro_verif": "الرمز غير صحيح. حاول مرة أخرى.",
        "add_cliente": "تسجيل عميل جديد",
        "nome_cliente": "اسم العميل",
        "email_cliente": "البريد الإلكتروني",
        "tel_cliente": "رقم الهاتف",
        "pais_cliente": "دولة العميل",
        "salvar": "حفظ التغييرات",
        "lista_clientes": "دليل العملاء المسجلين",
        "add_produto": "إضافة منتج جديد",
        "nome_produto": "اسم المنتج",
        "preco_produto": "السعر",
        "lista_produtos": "المنتجات المتوفرة",
        "reg_venda": "تسجيل عملية بيع",
        "qtd": "الكمية",
        "total_venda": "إجمالي المبيعات",
        "historico_vendas": "سجل المبيعات",
        "chat_ia": "تحدث مع مساعد الذكاء الاصطناعي",
        "pergunta_ia": "اكتب سؤال الإدارة الخاص بك:",
        "enviar": "إرسال السؤال",
        "sair": "تسجيل الخروج",
        "empresa_setup": "ملف الشركة والتسجيل",
    },
    "Deutsch (German)": {
        "titulo": "🚀 A Evolution Online-Management",
        "menu": "Hauptmenü",
        "clientes": "Kundenverwaltung",
        "produtos": "Produktverwaltung",
        "vendas": "Verkauf & Rechnungsstellung",
        "dashboard": "Dashboard & Konsolidierte Berichte",
        "config": "Regionale Einstellungen & Zahlungen",
        "ia": "KI-Assistent",
        "verificacao": "Sicherheit - E-Mail-Verifizierung",
        "enviar_codigo": "Verifizierungscode senden",
        "email_label": "Empfänger-E-Mail-Adresse",
        "codigo_label": "Erhaltenen Code eingeben (6 Ziffern)",
        "verificar": "Validieren und Anmelden",
        "sucesso_envio": "Code erfolgreich an den Posteingang gesendet!",
        "sucesso_verif": "Zugriff erfolgreich gewährt!",
        "erro_verif": "Falscher Code. Versuchen Sie es erneut.",
        "add_cliente": "Neuen Kunden registrieren",
        "nome_cliente": "Kundenname",
        "email_cliente": "E-Mail-Adresse",
        "tel_cliente": "Telefonnummer",
