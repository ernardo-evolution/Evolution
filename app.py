import streamlit as st
import random
import smtplib
from email.message import EmailMessage

# --- CONFIGURAÇÃO DA BREVO (SMTP) ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "bd480d001@smtp-brevo.com"
SMTP_PASSWORD = "xsmtpsib-d096c91441191fa127af74c066bf671fd22a2d8f1388e83b881f83ada76828cc-I53yeTW1epMDyC4w"  # Substitui pelo código longo que copiaste da Brevo

def enviar_codigo_por_email(destinatario, codigo):
    """Envia o código de verificação de 6 dígitos via Brevo SMTP para o e-mail real do utilizador."""
    msg = EmailMessage()
    msg.set_content(
        f"Olá!\n\nO teu código de verificação para o Evolution Gestão Online é: {codigo}\n\n"
        "Usa este código na aplicação para concluir o teu acesso com segurança."
    )
    msg["Subject"] = "🔐 Código de Verificação - Evolution Gestão Online"
    msg["From"] = SMTP_USER
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro detalhado no envio SMTP: {e}")
        return False

# --- LÓGICA DE VALIDAÇÃO DE SEGURANÇA NO APP ---
def executar_validacao_seguranca(email_utilizador):
    st.markdown("## 🛡️ Validação de Segurança do Sistema")
    st.write(f"Insira o código de 6 dígitos enviado para o e-mail: **{email_utilizador}**")

    # Gerar código se ainda não existir na sessão
    if "codigo_verificacao" not in st.session_state:
        codigo_gerado = str(random.randint(100000, 999999))
        st.session_state["codigo_verificacao"] = codigo_gerado
        
        # Tenta enviar o e-mail real através da Brevo
        sucesso = enviar_codigo_por_email(email_utilizador, codigo_gerado)
        st.session_state["email_enviado_sucesso"] = sucesso

    # Feedback visual para o utilizador
    if st.session_state.get("email_enviado_sucesso"):
        st.success("✉️ O código de verificação foi enviado com sucesso para a tua caixa de correio!")
    else:
        st.warning(
            "⚠️ Não foi possível enviar o e-mail automaticamente. "
            f"Código de teste para esta sessão: **{st.session_state['codigo_verificacao']}**"
        )

    # Input do código pelo utilizador
    codigo_inserido = st.text_input("Código de verificação", type="default")

    if st.button("Confirmar Código"):
        if codigo_inserido == st.session_state["codigo_verificacao"]:
            st.success("🎉 Código confirmado com sucesso! Acedendo ao sistema...")
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("❌ Código incorreto. Tenta novamente ou gera um novo código.")

    if st.button("Gerar Novo Código"):
        st.session_state["codigo_verificacao"] = str(random.randint(100000, 999999))
        sucesso = enviar_codigo_por_email(email_utilizador, st.session_state["codigo_verificacao"])
        st.session_state["email_enviado_sucesso"] = sucesso
        st.rerun()

# --- EXEMPLO DE FLUXO NO STREAMLIT ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    # E-mail de teste configurado
    executar_validacao_seguranca("bernardobonfim.reis26@gmail.com")
else:
    st.title("🚀 Evolution Gestão Online (v3.8.1)")
    st.write("Bem-vindo ao painel principal do sistema empresarial!")
