from datetime import datetime
import os
import random
import sqlite3
import pycountry
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
            "Brazil",
            "Brazil",
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
      "pais": "Brazil",
      "pais_registro": "Brazil",
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


# --- LISTA COMPLETA DE TODOS OS PAÍSES DO MUNDO VIA PYCOUNTRY ---
def obter_todos_os_paises():
  paises = sorted(
      [country.name for country in pycountry.countries], key=str.lower
  )
  return paises


# --- DICIONÁRIO MULTILÍNGUA ABRANGENTE (EM ORDEM ALFABÉTICA) ---
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
        "qtd": "Количество",
        "total_venda": "Общий объем продаж",
        "historico_vendas": "История продаж",
        "chat_ia": "Чат с ИИ-ассистентом",
        "pergunta_ia": "Введите ваш вопрос по управлению:",
        "enviar": "Отправить вопрос",
        "sair": "Выйти",
        "empresa_setup": "Профиль компании и регистрация",
    },
    "中文 (Chinese)": {
        "titulo": "🚀 A Evolution 在线管理系统",
        "menu": "主菜单",
        "clientes": "客户管理",
        "produtos": "产品管理",
        "vendas": "销售与开票",
        "dashboard": "仪表盘与综合报表",
        "config": "区域设置与支付",
        "ia": "AI 助手",
        "verificacao": "安全 - 电子邮件验证",
        "enviar_codigo": "发送验证码",
        "email_label": "收件人电子邮箱",
        "codigo_label": "输入收到的验证码（6位数字）",
        "verificar": "验证并登录",
        "sucesso_envio": "验证码已成功发送至收件箱！",
        "sucesso_verif": "成功授权访问！",
        "erro_verif": "验证码错误。请重试。",
        "add_cliente": "注册新客户",
        "nome_cliente": "客户姓名",
        "email_cliente": "电子邮箱",
        "tel_cliente": "电话号码",
        "pais_cliente": "客户国家",
        "salvar": "保存更改",
        "lista_clientes": "已注册客户名录",
        "add_produto": "添加新产品",
        "nome_produto": "产品名称",
        "preco_produto": "价格",
        "lista_produtos": "现有库存产品",
        "reg_venda": "记录销售",
        "qtd": "数量",
        "total_venda": "总销售额",
        "historico_vendas": "销售历史",
        "chat_ia": "与 AI 助手对话",
        "pergunta_ia": "输入您的管理问题：",
        "enviar": "发送问题",
        "sair": "退出登录",
        "empresa_setup": "公司资料与注册",
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

# Garantir robustez caso o idioma salvo não exista no dicionário
if idioma_selecionado not in DICIONARIO:
  idioma_selecionado = "Português"

t = DICIONARIO[idioma_selecionado]


# --- FUNÇÃO DE FORMATAÇÃO MONETÁRIA REATIVA GLOBAL ---
def formatar_moeda(valor, simbolo=simbolo_ativo):
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
  idioma_atual_idx = (
      idiomas_ordenados.index(idioma_selecionado)
      if idioma_selecionado in idiomas_ordenados
      else 0
  )
  idioma_sidebar = st.selectbox(
      "Idioma / Language", idiomas_ordenados, index=idioma_atual_idx
  )
  
  # Se o usuário mudar o idioma na barra lateral, atualizamos instantaneamente a sessão da empresa
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

  if menu == t["clientes"]:
    st.header(t["clientes"])
    
    with st.form("form_cliente"):
      st.subheader(t["add_cliente"])
      nome_cli = st.text_input(t["nome_cliente"])
      email_cli = st.text_input(t["email_cliente"])
      tel_cli = st.text_input(t["tel_cliente"])
      
      paises_lista_completa = obter_todos_os_paises()
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
                  1.0,
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
      
      # Carregar todos os países do mundo via pycountry
      paises_lista_completa = obter_todos_os_paises()
      
      pais_atual_idx = paises_lista_completa.index(emp["pais"]) if emp["pais"] in paises_lista_completa else 0
      
      novo_pais = st.selectbox("País de Operação", paises_lista_completa, index=pais_atual_idx)
      novo_pais_registro = st.selectbox(
          "País de Registo", paises_lista_completa, index=paises_lista_completa.index(emp["pais_registro"]) if emp["pais_registro"] in paises_lista_completa else 0
      )

      # Seleção independente de Moeda e Símbolo
      col_m1, col_m2 = st.columns(2)
      with col_m1:
        nova_moeda = st.text_input("Código da Moeda (ISO 4217)", value=emp["moeda"])
      with col_m2:
        novo_simbolo = st.text_input("Símbolo Monetário", value=emp["simbolo"])

      st.info(f"💱 Configuração Ativa: País **{novo_pais}** | Moeda **{nova_moeda} ({novo_simbolo})**")

      if st.form_submit_button(t["salvar"]):
        dados_atualizados = {
            "nome": novo_nome_empresa,
            "pais": novo_pais,
            "pais_registro": novo_pais_registro,
            "moeda": nova_moeda,
            "simbolo": novo_simbolo,
            "idioma": idioma_selecionado,
            "fuso": emp["fuso"],
        }
        salvar_empresa_db(dados_atualizados)
        st.success("Configurações atualizadas globalmente!")
        st.rerun()

    st.markdown("---")
    st.subheader("💳 Métodos de Pagamento Regionais")
    st.write(f"🟢 **PayPal Internacional & Transferência Bancária ({emp['moeda']})**")
    st.write("🟢 **Cartões de Crédito Globais (Visa/Mastercard/Amex)**")

    st.markdown("---")
    st.subheader("💱 Conversor Cambial de Teste")
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
