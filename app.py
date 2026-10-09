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
  # Tabela Empresa com preferências independentes
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
  # Tabela Clientes com cadastro detalhado
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            pais TEXT
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
            taxa_aplicada TEXT,
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
        "pais_cliente": "Kundenland",
        "salvar": "Änderungen speichern",
        "lista_clientes": "Registriertes Kundenverzeichnis",
        "add_produto": "Neues Produkt hinzufügen",
        "nome_produto": "Produktname",
        "preco_produto": "Preis",
        "lista_produtos": "Produkte auf Lager",
        "reg_venda": "Verkauf registrieren",
        "qtd": "Menge",
        "total_venda": "Gesamtverkäufe",
        "historico_vendas": "Verlauf der Verkäufe",
        "chat_ia": "Chat mit KI-Assistent",
        "pergunta_ia": "Geben Sie Ihre Managementfrage ein:",
        "enviar": "Frage senden",
        "sair": "Abmelden",
        "empresa_setup": "Unternehmensprofil & Registrierung",
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
        "verificacao": "Segurança - Verificación de Correo",
        "enviar_codigo": "Enviar Código de Verificación",
        "email_label": "Correo Electrónico del Destinatario",
        "codigo_label": "Ingrese el código recibido (6 dígitos)",
        "verificar": "Validar y Entrar",
        "sucesso_envio": "¡Código enviado con éxito a la bandeja de entrada!",
        "sucesso_verif": "¡Acceso autorizado com éxito!",
        "erro_verif": "Código incorrecto. Inténtelo de nuevo.",
        "add_cliente": "Registrar Nuevo Cliente",
        "nome_cliente": "Nombre del Cliente",
        "email_cliente": "Correo Electrónico",
        "tel_cliente": "Teléfono",
        "pais_cliente": "País del Cliente",
        "salvar": "Guardar Cambios",
        "lista_clientes": "Directorio de Clientes Registrados",
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
    "Français (French)": {
        "titulo": "🚀 A Evolution Gestion en Ligne",
        "menu": "Menu Principal",
        "clientes": "Gestion des Clients",
        "produtos": "Gestion des Produits",
        "vendas": "Ventes et Facturation",
        "dashboard": "Tableau de Bord & Rapports Consolidés",
        "config": "Paramètres Régionaux & Paiements",
        "ia": "Assistant IA",
        "verificacao": "Sécurité - Vérification par E-mail",
        "enviar_codigo": "Envoyer le Code de Vérification",
        "email_label": "Adresse E-mail du Destinataire",
        "codigo_label": "Entrez le code reçu (6 chiffres)",
        "verificar": "Valider et Se Connecter",
        "sucesso_envio": "Code envoyé avec succès dans la boîte de réception !",
        "sucesso_verif": "Accès autorisé avec succès !",
        "erro_verif": "Code incorrect. Réessayez.",
        "add_cliente": "Enregistrer un Nouveau Client",
        "nome_cliente": "Nom du Client",
        "email_cliente": "Adresse E-mail",
        "tel_cliente": "Numéro de Téléphone",
        "pais_cliente": "Pays du Client",
        "salvar": "Enregistrer les Modifications",
        "lista_clientes": "Répertoire des Clients Enregistrés",
        "add_produto": "Ajouter un Nouveau Produit",
        "nome_produto": "Nom du Produit",
        "preco_produto": "Prix",
        "lista_produtos": "Produits en Stock",
        "reg_venda": "Enregistrer la Vente",
        "qtd": "Quantité",
        "total_venda": "Ventes Totales",
        "historico_vendas": "Historique des Ventes",
        "chat_ia": "Discuter avec l'Assistant IA",
        "pergunta_ia": "Tapez votre question de gestion :",
        "enviar": "Envoyer la Question",
        "sair": "Se Déconnecter",
        "empresa_setup": "Profil & Enregistrement de l'Entreprise",
    },
    "日本語 (Japanese)": {
        "titulo": "🚀 A Evolution オンライン管理",
        "menu": "メインメニュー",
        "clientes": "顧客管理",
        "produtos": "商品管理",
        "vendas": "売上・請求",
        "dashboard": "ダッシュボード・統合レポート",
        "config": "地域設定・支払い",
        "ia": "AIアシスタント",
        "verificacao": "セキュリティ - メール認証",
        "enviar_codigo": "認証コードを送信",
        "email_label": "受信者のメールアドレス",
        "codigo_label": "受信したコードを入力（6桁）",
        "verificar": "確認してログイン",
        "sucesso_envio": "コードが正常に送信されました！",
        "sucesso_verif": "アクセスが正常に許可されました！",
        "erro_verif": "コードが正しくありません。もう一度お試しください。",
        "add_cliente": "新規顧客を登録",
        "nome_cliente": "顧客名",
        "email_cliente": "メールアドレス",
        "tel_cliente": "電話番号",
        "pais_cliente": "顧客の国",
        "salvar": "変更を保存",
        "lista_clientes": "登録済み顧客ディレクトリ",
        "add_produto": "新商品を追加",
        "nome_produto": "商品名",
        "preco_produto": "価格",
        "lista_produtos": "在庫商品",
        "reg_venda": "売上を登録",
        "qtd": "数量",
        "total_venda": "総売上",
        "historico_vendas": "売上履歴",
        "chat_ia": "AIアシスタントとチャット",
        "pergunta_ia": "管理に関する質問を入力してください：",
        "enviar": "質問を送信",
        "sair": "サインアウト",
        "empresa_setup": "企業プロフィール・登録",
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
    "Русский (Russian)": {
        "titulo": "🚀 A Evolution Онлайн Управление",
        "menu": "Главное меню",
        "clientes": "Управление клиентами",
        "produtos": "Управление продуктами",
        "vendas": "Продажи и выставление счетов",
        "dashboard": "Панель приборов и сводные отчеты",
        "config": "Региональные настройки и платежи",
        "ia": "ИИ-ассистент",
        "verificacao": "Безопасность - Подтверждение по электронной почте",
        "enviar_codigo": "Отправить код подтверждения",
        "email_label": "Электронная почта получателя",
        "codigo_label": "Введите полученный код (6 цифр)",
        "verificar": "Подтвердить и войти",
        "sucesso_envio": "Код успешно отправлен!",
        "sucesso_verif": "Доступ успешно предоставлен!",
        "erro_verif": "Неверный код. Попробуйте еще раз.",
        "add_cliente": "Зарегистрировать нового клиента",
        "nome_cliente": "Имя клиента",
        "email_cliente": "Электронная почта",
        "tel_cliente": "Номер телефона",
        "pais_cliente": "Страна клиента",
        "salvar": "Сохранить изменения",
        "lista_clientes": "Каталог зарегистрированных клиентов",
        "add_produto": "Добавить новый продукт",
        "nome_produto": "Название продукта",
        "preco_produto": "Цена",
        "lista_produtos": "Товары на складе",
        "reg_venda": "Зарегистрировать продажу",
