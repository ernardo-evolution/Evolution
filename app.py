import random
import resend
import streamlit as st

# Configura a chave do Resend de forma segura através dos segredos do Streamlit
# (Certifica-te de que adicionaste RESEND_API_KEY no secrets.toml do Streamlit Cloud)
try:
  resend.api_key = st.secrets["RESEND_API_KEY"]
except Exception:
  # Fallback caso estejas a testar localmente ou a configurar
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
                    <p style="font-size: 16px; color: #374151;">O seu código de verificação para acesso seguro ao sistema é:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: #ffffff; padding: 15px 25px; border-radius: 6px; border-left: 4px solid #2563eb; font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #111827; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            {codigo}
                        </div>
                    </div>
                    <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">Se não solicitou este código, por favor ignore esta mensagem.</p>
                </div>
            """,
    }

    response = resend.Emails.send(params)
    return True
  except Exception as e:
    st.error(f"Erro ao enviar e-mail pelo Resend: {e}")
    return False


# --- EXEMPLO DE FLUXO NA APLICAÇÃO ---
st.title("Evolution Gestão Online (v3.8.1)")
st.subheader("Painel de Acesso Seguro com Resend")

# Estado da sessão para controlar o fluxo de verificação
if "etapa" not in st.session_state:
  st.session_state.etapa = "login"
if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = None
if "email_utilizador" not in st.session_state:
  st.session_state.email_utilizador = ""

if st.session_state.etapa == "login":
  st.write("Insira o seu e-mail para receber o código de verificação:")
  email_input = st.text_input("E-mail corporativo", value="")

  if st.button("Enviar Código de Verificação"):
    if email_input:
      # Gerar código aleatório de 6 dígitos
      codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
      st.session_state.codigo_gerado = codigo
      st.session_state.email_utilizador = email_input

      with st.spinner("A enviar e-mail através do Resend..."):
        sucesso = enviar_codigo_verificacao(email_input, codigo)

      if sucesso:
        st.success(
            "Código enviado com sucesso! Verifique a sua caixa de entrada."
        )
        st.session_state.etapa = "verificar"
        st.rerun()
    else:
      st.warning("Por favor, insira um e-mail válido.")

elif st.session_state.etapa == "verificar":
  st.info(f"Enviámos um código de 6 dígitos para: **{st.session_state.email_utilizador}**")
  codigo_digitado = st.text_input("Insira o código de verificação", max_chars=6)

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Confirmar Código"):
      if codigo_digitado == st.session_state.codigo_gerado:
        st.success("Autenticação efetuada com sucesso! Bem-vindo ao Evolution Gestão Online.")
        st.session_state.etapa = "dashboard"
        st.rerun()
      else:
        st.error("Código incorreto. Tente novamente.")

  with col2:
    if st.button("Reenviar Código"):
      codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
      st.session_state.codigo_gerado = codigo
      if enviar_codigo_verificacao(st.session_state.email_utilizador, codigo):
        st.success("Novo código enviado!")

elif st.session_state.etapa == "dashboard":
  st.balloons()
  st.markdown("### 📊 Bem-vindo ao Dashboard Principal")
  st.write("O seu sistema está conectado e a funcionar perfeitamente com o Resend.")
  
  if st.button("Terminar Sessão"):
    st.session_state.etapa = "login"
    st.session_state.codigo_gerado = None
    st.session_state.email_utilizador = ""
    st.rerun()
