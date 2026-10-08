import resend
import streamlit as st

# Configura a chave do Resend de forma segura através dos segredos
resend.api_key = st.secrets["RESEND_API_KEY"]


def enviar_codigo_verificacao(email_destino, codigo):
  try:
    params = {
        "from": "Evolution Gestão <onboarding@resend.dev>",
        "to": [email_destino],
        "subject": "Código de Verificação - Evolution Gestão Online",
        "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafb; border-radius: 8px;">
                    <h2 style="color: #1e3a8a;">Evolution Gestão Online</h2>
                    <p>Olá! O seu código de verificação para acesso seguro é:</p>
                    <div style="background: #ffffff; padding: 15px; border-left: 4px solid #2563eb; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #111827; display: inline-block;">
                        {codigo}
                    </div>
                    <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">Se não solicitou este código, ignore esta mensagem.</p>
                </div>
            """,
    }

    response = resend.Emails.send(params)
    return True
  except Exception as e:
    st.error(f"Erro ao enviar e-mail pelo Resend: {e}")
    return False
