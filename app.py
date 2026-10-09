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

# --- DICIONÁRIO MULTILÍNGUA (PT, EN, ES) ---
DICIONARIO = {
    "Português": {
        "titulo": "🚀 A Evolution Gestão Online",
        "idioma": "Idioma",
        "menu": "Menu Principal",
        "clientes": "Gestão de Clientes",
        "produtos": "Gestão de Produtos",
        "ia": "Assistente IA",
        "verificacao": "Verificação de E-mail",
        "enviar_codigo": "Enviar Código de Verificação",
        "email_label": "Insira o e-mail do cliente/destinatário:",
        "codigo_label": "Insira o código recebido:",
        "verificar": "Verificar Código",
        "sucesso_envio": "Código enviado com sucesso para a caixa de entrada do destinatário!",
        "sucesso_verif": "Acesso autorizado com sucesso!",
        "erro_verif": "Código incorreto. Tente novamente.",
        "add_cliente": "Adicionar Novo Cliente",
        "nome_cliente": "Nome do Cliente",
        "salvar": "Salvar",
        "lista_clientes": "Clientes Registados",
        "add_produto": "Adicionar Novo Produto",
        "nome_produto": "Nome do Produto",
        "preco_produto": "Preço (€)",
        "lista_produtos": "Produtos em Stock",
        "chat_ia": "Converse com o Assistente IA",
        "pergunta_ia": "Escreva a sua dúvida sobre gestão:",
        "enviar": "Enviar Pergunta",
    },
    "English": {
        "titulo": "🚀 A Evolution Online Management",
        "idioma": "Language",
        "menu": "Main Menu",
        "clientes": "Client Management",
        "produtos": "Product Management",
        "ia": "AI Assistant",
        "verificacao": "Email Verification",
        "enviar_codigo": "Send Verification Code",
        "email_label": "Enter client/recipient email:",
        "codigo_label": "Enter received code:",
        "verificar": "Verify Code",
        "sucesso_envio": "Code successfully sent to the recipient's inbox!",
        "sucesso_verif": "Access granted successfully!",
        "erro_verif": "Incorrect code. Try again.",
        "add_cliente": "Add New Client",
        "nome_cliente": "Client Name",
        "salvar": "Save",
        "lista_clientes": "Registered Clients",
        "add_produto": "Add New Product",
        "nome_produto": "Product Name",
        "preco_produto": "Price ($)",
        "lista_produtos": "Products in Stock",
        "chat_ia": "Chat with AI Assistant",
        "pergunta_ia": "Type your management question:",
        "enviar": "Send Question",
    },
    "Español": {
        "titulo": "🚀 A Evolution Gestión Online",
        "idioma": "Idioma",
        "menu": "Menú Principal",
        "clientes": "Gestión de Clientes",
        "produtos": "Gestión de Productos",
        "ia": "Asistente IA",
        "verificacao": "Verificación de Correo",
        "enviar_codigo": "Enviar Código de Verificación",
        "email_label": "Ingrese el correo del cliente/destinatario:",
        "codigo_label": "Ingrese el código recibido:",
        "verificar": "Verificar Código",
        "sucesso_envio": (
            "¡Código enviado con éxito a la bandeja de entrada del"
            " destinatario!"
        ),
        "sucesso_verif": "¡Acceso autorizado con éxito!",
        "erro_verif": "Código incorrecto. Inténtelo de nuevo.",
        "add_cliente": "Añadir Nuevo Cliente",
        "nome_cliente": "Nombre del Cliente",
        "salvar": "Guardar",
        "lista_clientes": "Clientes Registrados",
        "add_produto": "Añadir Nuevo Producto",
        "nome_produto": "Nombre del Producto",
        "preco_produto": "Precio (€)",
        "lista_produtos": "Productos en Stock",
        "chat_ia": "Chatea con el Asistente IA",
        "pergunta_ia": "Escribe tu duda de gestión:",
        "enviar": "Enviar Pregunta",
    },
}

# --- SELETOR DE IDIOMA NA BARRA LATERAL ---
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/combo-chart--v1.png", width=80
  )  # Ícone representativo
  idioma_atual = st.selectbox("Idioma / Language", ["Português", "English", "Español"])
  t = DICIONARIO[idioma_atual]

  st.markdown("---")
  menu = st.radio(
      t["menu"], [t["verificacao"], t["clientes"], t["produtos"], t["ia"]]
  )

# --- ESTADOS DA SESSÃO ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
if "codigo_enviado" not in st.session_state:
  st.session_state["codigo_enviado"] = ""
if "clientes" not in st.session_state:
  st.session_state["clientes"] = []
if "produtos" not in st.session_state:
  st.session_state["produtos"] = []

# --- TÍTULO PRINCIPAL ---
st.title(t["titulo"])

# --- FUNÇÃO DE ENVIO EMAILJS ---
def disparar_emailjs(email_destino, codigo):
  payload = {
      "service_id": SERVICE_ID,
      "template_id": TEMPLATE_ID,
      "user_id": USER_ID,
      "accessToken": ACCESS_TOKEN,
      "template_params": {
          "to_email": email_destino,  # Garante envio direto para a outra pessoa
          "email": email_destino,
          "codigo": codigo,
      },
  }
  try:
    resposta = requests.post(EMAILJS_URL, json=payload)
    return resposta.status_code == 200
  except:
    return False


# --- MÓDULO 1: VERIFICAÇÃO DE E-MAIL (DESTINATÁRIO EXTERNO) ---
if menu == t["verificacao"]:
  st.header(t["verificacao"])

  if not st.session_state["autenticado"]:
    email_input = st.text_input(t["email_label"])

    if st.button(t["enviar_codigo"]):
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
      if st.button(t["verificar"]):
        if codigo_digitado == st.session_state["codigo_enviado"]:
          st.session_state["autenticado"] = True
          st.success(t["sucesso_verif"])
          st.rerun()
        else:
          st.error(t["erro_verif"])
  else:
    st.success("✅ Sistema desbloqueado e pronto a utilizar!")
    if st.button("Terminar Sessão / Bloquear"):
      st.session_state["autenticado"] = False
      st.session_state["codigo_enviado"] = ""
      st.rerun()

# --- MÓDULO 2: GESTÃO DE CLIENTES ---
elif menu == t["clientes"]:
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

# --- MÓDULO 3: GESTÃO DE PRODUTOS ---
elif menu == t["produtos"]:
  st.header(t["produtos"])
  nome_prod = st.text_input(t["nome_produto"])
  preco_prod = st.number_input(t["preco_produto"], min_value=0.0, format="%.2f")

  if st.button(t["salvar"]):
    if nome_prod:
      st.session_state["produtos"].append(
          {"nome": nome_prod, "preco": preco_prod}
      )
      st.success(f"Produto '{nome_prod}' adicionado com sucesso!")
    else:
      st.warning("Insira o nome do produto.")

  st.subheader(t["lista_produtos"])
  for prod in st.session_state["produtos"]:
    st.write(f"- **{prod['nome']}**: {prod['preco']} €")

# --- MÓDULO 4: ASSISTENTE IA ---
elif menu == t["ia"]:
  st.header(t["chat_ia"])
  pergunta = st.text_input(t["pergunta_ia"])
  if st.button(t["enviar"]):
    if pergunta:
      # Resposta simulada inteligente para o assistente de gestão
      st.info(
          f"💡 **IA Evolution:** Analisando a sua questão sobre gestão ('{pergunta}'),"
          " recomendo manter o foco na otimização de custos e acompanhamento"
          " próximo dos seus clientes registados."
      )
    else:
      st.warning("Escreva uma pergunta.")
