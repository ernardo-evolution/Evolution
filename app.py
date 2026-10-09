from datetime import datetime
import random
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

# --- BASE INTERNACIONAL DE PAÍSES E MOEDAS ---
PAISES_MOEDAS = {
    "Brasil": {"codigo": "BR", "moeda": "BRL", "simbolo": "R$", "idioma": "Português", "fuso": "UTC-3"},
    "Estados Unidos": {"codigo": "US", "moeda": "USD", "simbolo": "US$", "idioma": "English", "fuso": "UTC-5"},
    "Portugal": {"codigo": "PT", "moeda": "EUR", "simbolo": "€", "idioma": "Português", "fuso": "UTC+0"},
    "Espanha": {"codigo": "ES", "moeda": "EUR", "simbolo": "€", "idioma": "Español", "fuso": "UTC+1"},
    "Reino Unido": {"codigo": "GB", "moeda": "GBP", "simbolo": "£", "idioma": "English", "fuso": "UTC+0"},
    "Japão": {"codigo": "JP", "moeda": "JPY", "simbolo": "¥", "idioma": "English", "fuso": "UTC+9"},
    "Canadá": {"codigo": "CA", "moeda": "CAD", "simbolo": "CA$", "idioma": "English", "fuso": "UTC-5"},
    "Austrália": {"codigo": "AU", "moeda": "AUD", "simbolo": "A$", "idioma": "English", "fuso": "UTC+10"},
    "México": {"codigo": "MX", "moeda": "MXN", "simbolo": "MX$", "idioma": "Español", "fuso": "UTC-6"},
    "Argentina": {"codigo": "AR", "moeda": "ARS", "simbolo": "ARS", "idioma": "Español", "fuso": "UTC-3"},
    "Suíça": {"codigo": "CH", "moeda": "CHF", "simbolo": "CHF", "idioma": "English", "fuso": "UTC+1"},
    "Índia": {"codigo": "IN", "moeda": "INR", "simbolo": "₹", "idioma": "English", "fuso": "UTC+5:30"},
    "China": {"codigo": "CN", "moeda": "CNY", "simbolo": "CN¥", "idioma": "English", "fuso": "UTC+8"},
    "África do Sul": {"codigo": "ZA", "moeda": "ZAR", "simbolo": "ZAR", "idioma": "English", "fuso": "UTC+2"},
    "Angola": {"codigo": "AO", "moeda": "AOA", "simbolo": "Kz", "idioma": "Português", "fuso": "UTC+1"},
    "Moçambique": {"codigo": "MZ", "moeda": "MZN", "simbolo": "MT", "idioma": "Português", "fuso": "UTC+2"},
    "Cabo Verde": {"codigo": "CV", "moeda": "CVE", "simbolo": "CVE", "idioma": "Português", "fuso": "UTC-1"},
    "Paraguai": {"codigo": "PY", "moeda": "PYG", "simbolo": "₲", "idioma": "Español", "fuso": "UTC-4"},
    "Uruguai": {"codigo": "UY", "moeda": "UYU", "simbolo": "$U", "idioma": "Español", "fuso": "UTC-3"},
}

# --- DICIONÁRIO MULTILÍNGUA COM ITENS EM ORDEM ALFABÉTICA ---
DICIONARIO = {
    "English": {
        "titulo": "🚀 A Evolution Online Management",
        "menu": "Main Menu",
        "clientes": "Client Management",
        "produtos": "Product Management",
        "ia": "AI Assistant",
        "config": "Regional Settings & Payments",
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
        "ia": "Asistente IA",
        "config": "Configuración Regional y Pagos",
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
        "lista_produtos": "Produtos en Stock",
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
        "ia": "Assistente IA",
        "config": "Configurações Regionais & Pagamentos",
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
if "clientes" not in st.session_state:
  st.session_state["clientes"] = []
if "produtos" not in st.session_state:
  st.session_state["produtos"] = []

# Configurações de Empresa (Padrão Brasil - BRL)
if "empresa" not in st.session_state:
  st.session_state["empresa"] = {
      "nome": "Evolution Corp Brasil",
      "pais": "Brasil",
      "pais_registro": "Brasil",
      "moeda": "BRL",
      "simbolo": "R$",
      "idioma": "Português",
      "fuso": "UTC-3",
  }


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
  # Idiomas ordenados alfabeticamente: English, Español, Português
  idiomas_ordenados = sorted(list(DICIONARIO.keys()))
  idioma_atual = st.selectbox("Idioma / Language", idiomas_ordenados)
  t = DICIONARIO[idioma_atual]

  if st.session_state["autenticado"]:
    st.markdown("---")
    
    # Itens do menu ordenados estritamente em ordem alfabética para cada idioma
    if idioma_atual == "English":
      opcoes_menu = [t["ia"], t["clientes"], t["config"], t["produtos"]]
    elif idioma_atual == "Español":
      opcoes_menu = [t["ia"], t["clientes"], t["config"], t["produtos"]]
    else:  # Português
      opcoes_menu = [t["ia"], t["clientes"], t["config"], t["produtos"]]
    
    # Ordenar alfabeticamente por nome da opção
    opcoes_menu = sorted(opcoes_menu)

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
  except:
    return False


# --- BLOCO DE SEGURANÇA / LOGIN (DUAS COLUNAS COM VETOR CORPORATIVO E SEM LEGENDA) ---
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
  emp = st.session_state["empresa"]
  simbolo_ativo = emp["simbolo"]

  if menu == t["clientes"]:
    st.header(t["clientes"])
    nome_cli = st.text_input(t["nome_cliente"])
    if st.button(t["salvar"]):
      if nome_cli:
        st.session_state["clientes"].append(nome_cli)
        st.success(f"Cliente '{nome_cli}' adicionado com sucesso!")
      else:
        st.warning("O nome não pode estar vazio.")

    st.subheader(t["lista_clientes"])
    for cli in st.session_state["clientes"]:
      st.write(f"- {cli}")

  elif menu == t["produtos"]:
    st.header(t["produtos"])
    nome_prod = st.text_input(t["nome_produto"])
    
    preco_prod = st.number_input(
        f"{t['preco_produto']} ({simbolo_ativo})", min_value=0.0, format="%.2f"
    )

    if st.button(t["salvar"]):
      if nome_prod:
        st.session_state["produtos"].append(
            {
                "nome": nome_prod,
                "preco": preco_prod,
                "moeda": emp["moeda"],
                "simbolo": simbolo_ativo,
            }
        )
        st.success(f"Produto '{nome_prod}' adicionado com sucesso!")
      else:
        st.warning("Insira o nome do produto.")

    st.subheader(t["lista_produtos"])
    for prod in st.session_state["produtos"]:
      valor_formatado = formatar_moeda(prod["preco"], prod["simbolo"])
      st.write(f"- **{prod['nome']}**: {valor_formatado}")

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
      nova_moeda =
