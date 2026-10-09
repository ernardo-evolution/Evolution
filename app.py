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
        "menu": "Menu Principal",
        "clientes": "Gestão de Clientes",
        "produtos": "Gestão de Produtos",
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
        "salvar": "Salvar",
        "lista_clientes": "Clientes Registados",
        "add_produto": "Adicionar Novo Produto",
        "nome_produto": "Nome do Produto",
        "preco_produto": "Preço (€)",
        "lista_produtos": "Produtos em Stock",
        "chat_ia": "Converse com o Assistente IA",
        "pergunta_ia": "Escreva a sua dúvida sobre gestão:",
        "enviar": "Enviar Pergunta",
        "sair": "Terminar Sessão",
    },
    "English": {
        "titulo": "🚀 A Evolution Online Management",
        "menu": "Main Menu",
        "clientes": "Client Management",
        "produtos": "Product Management",
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
        "salvar": "Save",
        "lista_clientes": "Registered Clients",
        "add_produto": "Add New Product",
        "nome_produto": "Product Name",
        "preco_produto": "Price ($)",
        "lista_produtos": "Products in Stock",
        "chat_ia": "Chat with AI Assistant",
        "pergunta_ia": "Type your management question:",
        "enviar": "Send Question",
        "sair": "Sign Out",
    },
    "Español": {
        "titulo": "🚀 A Evolution Gestión Online",
        "menu": "Menú Principal",
        "clientes": "Gestión de Clientes",
        "produtos": "Gestión de Productos",
        "ia": "Asistente IA",
        "verificacao": "Seguridad - Verificación de Correo",
        "enviar_codigo": "Enviar Código de Verificación",
        "email_label": "Correo Electrónico del Destinatario",
        "codigo_label": "Ingrese el código recibido (6 dígitos)",
        "verificar": "Validar y Entrar",
        "sucesso_envio": "¡Código enviado con éxito a la bandeja de entrada!",
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
        "sair": "Cerrar Sesión",
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

# --- SELETOR DE IDIOMA NA BARRA LATERAL ---
with st.sidebar:
  st.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=70)
  idioma_atual = st.selectbox("Idioma / Language", ["Português", "English", "Español"])
  t = DICIONARIO[idioma_atual]

  # O menu só aparece se o utilizador já estiver autenticado
  if st.session_state["autenticado"]:
    st.markdown("---")
    menu = st.radio(
        t["menu"], [t["clientes"], t["produtos"], t["ia"]]
    )
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
          "to_email": email_destino,  # Vai direto para o e-mail da outra pessoa
          "email": email_destino,
          "codigo": codigo,
      },
  }
  try:
    resposta = requests.post(EMAILJS_URL, json=payload)
    return resposta.status_code == 200
  except:
    return False


# --- BLOCO DE SEGURANÇA / LOGIN (ESTILO DUAS COLUNAS COM IMAGEM) ---
if not st.session_state["autenticado"]:
  st.title(t["titulo"])
  st.markdown("### Acesso Restrito - Validação por E-mail")
  
  # Criamos duas colunas imitando o layout das tuas referências (Formulário vs Imagem/Plantas)
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
    # Imagem decorativa de plantas/estética corporativa tal como pediste no estilo da imagem 2
    st.image(
        "https://images.unsplash.com/photo-1545241047-6083a3684587?q=80&w=1000&auto=format&fit=crop",
        caption="A Evolution Gestão Online - Segurança em Primeiro Lugar",
        use_column_width=True
    )

# --- APLICAÇÃO PRINCIPAL (SÓ ABRE APÓS AUTENTICAÇÃO BEM-SUCEDIDA) ---
else:
  st.title(t["titulo"])

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

  elif menu == t["ia"]:
    st.header(t["chat_ia"])
    pergunta = st.text_input(t["pergunta_ia"])
    if st.button(t["enviar"]):
      if pergunta:
        st.info(
            f"💡 **IA Evolution:** Analisando a sua questão sobre gestão ('{pergunta}'),"
            " recomendo manter o foco na otimização de custos e acompanhamento"
            " próximo dos seus clientes registados."
        )
      else:
        st.warning("Escreva uma pergunta.")
