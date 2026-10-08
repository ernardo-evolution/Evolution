import streamlit as st
import random
import smtplib
from datetime import date
from email.message import EmailMessage

# --- CONFIGURAÇÃO DA BREVO (SMTP) ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "bd480d001@smtp-brevo.com"
SMTP_PASSWORD = "xsmtpsib-d096c91441191fa127af74c066bf671fd22a2d8f1388e83b881f83ada76828cc-0WmgMavC2wbzsRqg"  # Substitui pela tua chave da Brevo

def enviar_codigo_por_email(destinatario, codigo):
    """Envia o código de verificação via Brevo SMTP."""
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
        st.error(f"❌ Erro detalhado da Brevo ao enviar: {e}")
        return False

# --- GESTÃO DE ESTADOS DO FLUXO ---
if "etapa" not in st.session_state:
    st.session_state["etapa"] = "capa"  # Etapas: 'capa', 'registo', 'verificacao', 'app'

if "utilizador" not in st.session_state:
    st.session_state["utilizador"] = {}

# ==========================================
# 1. PÁGINA DE CAPA
# ==========================================
if st.session_state["etapa"] == "capa":
    st.title("🚀 Evolution Gestão Online")
    st.write("### O teu sistema empresarial inteligente e seguro (v3.8.1)")
    st.write("Gerencia o teu negócio com total eficiência e proteção de dados.")
    
    if st.button("Aceder / Registar no Sistema", type="primary"):
        st.session_state["etapa"] = "registo"
        st.rerun()

# ==========================================
# 2. PÁGINA DE REGISTO / LOGIN
# ==========================================
elif st.session_state["etapa"] == "registo":
    st.markdown("## 📝 Registo de Utilizador")
    
    with st.form("form_registo"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail para contacto e verificação")
        data_nascimento = st.date_input("Data de nascimento", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
        
        submetido = st.form_submit_button("Continuar para Verificação")
        
        if submetido:
            if not nome or not email:
                st.error("⚠️ Por favor, preenche o nome e o e-mail.")
            else:
                # Calcular se é maior de idade (18 anos)
                hoje = date.today()
                idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
                
                if idade < 18:
                    st.error("❌ Tens de ser maior de idade (18 anos) para aceder a esta plataforma.")
                else:
                    # Guardar dados na sessão
                    st.session_state["utilizador"]["nome"] = nome
                    st.session_state["utilizador"]["email"] = email
                    
                    # Gerar e enviar o código de verificação por e-mail
                    codigo_gerado = str(random.randint(100000, 999999))
                    st.session_state["codigo_verificacao"] = codigo_gerado
                    
                    with st.spinner("A enviar o código de verificação para o teu e-mail..."):
                        sucesso = enviar_codigo_por_email(email, codigo_gerado)
                    
                    if sucesso:
                        st.success("✉️ E-mail enviado com sucesso! Redirecionando...")
                        st.session_state["etapa"] = "verificacao"
                        st.rerun()
                    else:
                        st.warning("⚠️ Ocorreu um pequeno erro ao disparar o e-mail, mas podes prosseguir com o código de segurança.")
                        st.session_state["etapa"] = "verificacao"
                        st.rerun()

# ==========================================
# 3. PÁGINA DE VERIFICAÇÃO POR E-MAIL
# ==========================================
elif st.session_state["etapa"] == "verificacao":
    st.markdown("## 🛡️ Validação de Segurança do Sistema")
    email_atual = st.session_state["utilizador"].get("email", "o teu e-mail")
    st.write(f"Insira o código de 6 dígitos enviado para: **{email_atual}**")

    codigo_inserido = st.text_input("Código de verificação", type="default")

    if st.button("Confirmar Código"):
        if codigo_inserido == st.session_state.get("codigo_verificacao"):
            st.success("🎉 Código confirmado com sucesso! Bem-vindo ao sistema.")
            st.session_state["etapa"] = "app"
            st.rerun()
        else:
            st.error("❌ Código incorreto. Tenta novamente.")

    if st.button("Gerar Novo Código"):
        novo_codigo = str(random.randint(100000, 999999))
        st.session_state["codigo_verificacao"] = novo_codigo
        enviar_codigo_por_email(email_atual, novo_codigo)
        st.success("✉️ Um novo código foi enviado para o teu e-mail!")

# ==========================================
# 4. PAINEL PRINCIPAL DO APP
# ==========================================
elif st.session_state["etapa"] == "app":
    nome_utilizador = st.session_state["utilizador"].get("nome", "Utilizador")
    st.title(f"🚀 Evolution Gestão Online (v3.8.1)")
    st.write(f"Olá, **{nome_utilizador}**! Bem-vindo ao painel principal do sistema empresarial.")
    
    if st.button("Terminar Sessão / Sair"):
        st.session_state.clear()
        st.rerun()
