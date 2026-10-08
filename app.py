import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Evolution Gestão Online", page_icon="🛡️", layout="centered"
)

# --- CARREGAR CREDENCIAIS DE FORMA SEGURA VIA SECRETS ---
try:
  SMTP_SERVER = st.secrets["smtp"]["server"]
  SMTP_PORT = st.secrets["smtp"]["port"]
  SMTP_USER = st.secrets["smtp"]["user"]
  SMTP_PASSWORD = st.secrets["smtp"]["password"]
except Exception as e:
  st.error(
      "Erro crítico: As credenciais SMTP não estão configuradas nos Secrets"
      " do Streamlit Cloud."
  )
  st.stop()


# --- FUNÇÃO DE ENVIO DE E-MAIL (BREVO SMTP) ---
def enviar_codigo_por_email(destinatario, codigo):
  try:
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = "Evolution Gestão Online - Código de Verificação"

    corpo = (
        f"Olá!\n\nO seu código de verificação para acesso ao Evolution Gestão"
        f" Online é: {codigo}\n\nSe não solicitou este código, ignore esta"
        " mensagem."
    )
    msg.attach(MIMEText(corpo, "plain"))

    # Conexão SMTP com a Brevo (Porta 587 com TLS)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, destinatario, msg.as_string())
    server.quit()
    return True
  except Exception as e:
    st.error(f"Erro detalhado da Brevo ao enviar: {e}")
    return False


# --- GESTÃO DE ESTADO DA SESSÃO ---
if "etapa" not in st.session_state:
  st.session_state.etapa = "capa"

if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = None

if "email_usuario" not in st.session_state:
  st.session_state.email_usuario = ""


# --- ETAPA 1: CAPA ---
if st.session_state.etapa == "capa":
  st.title("🛡️ Evolution Gestão Online")
  st.subheader("Enterprise SaaS Platform (v3.8.1)")
  st.write(
      "Bem-vindo ao sistema de gestão de alta performance. Clique no botão"
      " abaixo para iniciar o seu registo seguro."
  )

  if st.button("Iniciar Registo"):
    st.session_state.etapa = "registo"
    st.rerun()


# --- ETAPA 2: REGISTO COM VALIDAÇÃO DE IDADE ---
elif st.session_state.etapa == "registo":
  st.title("📝 Registo de Novo Utilizador")

  nome = st.text_input("Nome Completo")
  email = st.text_input("E-mail corporativo ou pessoal")
  idade = st.number_input("Idade", min_value=1, max_value=120, value=18)

  if st.button("Avançar para Verificação"):
    if not nome or not email:
      st.warning("Por favor, preencha todos os campos.")
    elif idade < 18:
      st.error(
          "Erro de Validação: O acesso ao sistema requer idade igual ou"
          " superior a 18 anos."
      )
    else:
      st.session_state.email_usuario = email
      # Gerar código de 6 dígitos
      codigo = str(random.randint(100000, 999999))
      st.session_state.codigo_gerado = codigo

      # Enviar o e-mail real via Brevo
      with st.spinner("A enviar código de verificação para o seu e-mail..."):
        sucesso = enviar_codigo_por_email(email, codigo)

      if sucesso:
        st.success("Um novo código foi enviado para o teu e-mail!")
        st.session_state.etapa = "verificacao"
        st.rerun()


# --- ETAPA 3: VALIDAÇÃO DO CÓDIGO DE SEGURANÇA ---
elif st.session_state.etapa == "verificacao":
  st.title("🔒 Validação de Segurança do Sistema")
  st.write(
      f"Insira o código de 6 dígitos enviado para:"
      f" **{st.session_state.email_usuario}**"
  )

  codigo_inserido = st.text_input(
      "Código de verificação", type="default", max_chars=6
  )

  col1, col2 = st.columns(2)

  with col1:
    if st.button("Confirmar Código"):
      if codigo_inserido == st.session_state.codigo_gerado:
        st.success("Autenticação bem-sucedida! A entrar no sistema...")
        st.session_state.etapa = "app_principal"
        st.rerun()
      else:
        st.error("Código incorreto. Tente novamente.")

  with col2:
    if st.button("Gerar Novo Código"):
      novo_codigo = str(random.randint(100000, 999999))
      st.session_state.codigo_gerado = novo_codigo
      if enviar_codigo_por_email(st.session_state.email_usuario, novo_codigo):
        st.success("Um novo código foi enviado para o teu e-mail!")


# --- ETAPA 4: APLICAÇÃO PRINCIPAL ---
elif st.session_state.etapa == "app_principal":
  st.title("🚀 Evolution Gestão Online - Painel Principal")
  st.success("Sessão autenticada com sucesso!")
  st.write(
      "Aqui tens acesso a todas as ferramentas corporativas da v3.8.1."
  )

  if st.button("Terminar Sessão"):
    st.session_state.etapa = "capa"
    st.session_state.codigo_gerado = None
    st.session_state.email_usuario = ""
    st.rerun()
