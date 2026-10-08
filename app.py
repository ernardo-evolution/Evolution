import random
import time
import resend
import streamlit as st

# Configura a chave do Resend
try:
  resend.api_key = st.secrets["RESEND_API_KEY"]
except Exception:
  resend.api_key = "coloca_aqui_a_tua_chave_se_necessario"


def enviar_codigo_verificacao(email_destino, codigo):
  """Envia o código de verificação de 6 dígitos utilizando a API do Resend."""
  try:
    params = {
        "from": "Evolution Gestão <onboarding@resend.dev>",
        "to": [email_destino],
        "subject": "Código de Verificação - Evolution Gestão Online",
        "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafb; border-radius: 8px; max-width: 600px; margin: auto;">
                    <h2 style="color: #1e3a8a; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Evolution Gestão Online</h2>
                    <p style="font-size: 16px; color: #374151;">Olá!</p>
                    <p style="font-size: 16px; color: #374151;">O seu código de verificação para acesso seguro é:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: #ffffff; padding: 15px 25px; border-radius: 6px; border-left: 4px solid #2563eb; font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #111827; display: inline-block;">
                            {codigo}
                        </div>
                    </div>
                </div>
            """,
    }
    resend.Emails.send(params)
    return True
  except Exception as e:
    st.error(f"Erro ao enviar e-mail: {e}")
    return False


# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(
    page_title="Evolution Gestão Online - A Evolution",
    page_icon="🚀",
    layout="centered",
)

# Estado da sessão
if "etapa" not in st.session_state:
  st.session_state.etapa = "login"
if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = None
if "email_utilizador" not in st.session_state:
  st.session_state.email_utilizador = ""
if "animacao_vista" not in st.session_state:
  st.session_state.animacao_vista = False

# --- FLUXO DE LOGIN / VERIFICAÇÃO ---
if st.session_state.etapa == "login":
  st.title("🚀 Evolution Gestão Online")
  st.subheader("A Evolution - Acesso Seguro")
  st.write("Insira o seu e-mail corporativo para receber o código de acesso:")

  email_input = st.text_input("E-mail", value="")

  if st.button("Enviar Código de Verificação"):
    if email_input:
      codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
      st.session_state.codigo_gerado = codigo
      st.session_state.email_utilizador = email_input

      with st.spinner("A enviar e-mail..."):
        sucesso = enviar_codigo_verificacao(email_input, codigo)

      if sucesso:
        st.success("Código enviado com sucesso! Verifique a sua caixa de entrada.")
        st.session_state.etapa = "verificar"
        st.rerun()
    else:
      st.warning("Por favor, insira um e-mail válido.")

elif st.session_state.etapa == "verificar":
  st.title("🔐 Verificação de Segurança")
  st.info(f"Enviámos um código para: **{st.session_state.email_utilizador}**")
  
  codigo_digitado = st.text_input("Insira o código de 6 dígitos", max_chars=6)

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Confirmar Código"):
      if codigo_digitado == st.session_state.codigo_gerado:
        st.session_state.etapa = "dashboard"
        st.session_state.animacao_vista = False  # Dispara a animação ao entrar
        st.rerun()
      else:
        st.error("Código incorreto.")

  with col2:
    if st.button("Reenviar"):
      codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
      st.session_state.codigo_gerado = codigo
      if enviar_codigo_verificacao(st.session_state.email_utilizador, codigo):
        st.success("Novo código enviado!")

elif st.session_state.etapa == "dashboard":
  # --- ANIMAÇÃO DE LANÇAMENTO DA NAVE (A EVOLUTION) ---
  if not st.session_state.animacao_vista:
    placeholder = st.empty()
    with placeholder.container():
      st.markdown(
          """
            <style>
            @keyframes launch {
                0% { transform: translateY(150px); opacity: 0; }
                50% { opacity: 1; }
                100% { transform: translateY(-50px); opacity: 0; }
            }
            .rocket-container {
                text-align: center;
                padding: 50px;
                font-size: 80px;
                animation: launch 2.5s ease-in-out forwards;
            }
            .empresa-title {
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                color: #2563eb;
                margin-top: -20px;
            }
            </style>
            <div class="rocket-container">🚀💨</div>
            <div class="empresa-title">A EVOLUTION - Gestão Online</div>
            """,
          unsafe_allow_html=True,
      )
      time.sleep(2.5)  # Duração da animação de descolagem
    placeholder.empty()
    st.session_state.animacao_vista = True
    st.rerun()

  # Conteúdo Principal do Dashboard
  st.balloons()
  st.title("🌟 Bem-vindo ao Dashboard - A Evolution")
  st.write("Sistema integrado com sucesso e pronto a operar!")

  if st.button("Terminar Sessão"):
    st.session_state.etapa = "login"
    st.session_state.codigo_gerado = None
    st.session_state.email_utilizador = ""
    st.session_state.animacao_vista = False
    st.rerun()
