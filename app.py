from datetime import datetime
import hashlib
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Evolution Gestão Online",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. DESIGN E CSS PROFISSIONAL (SAAS) ---
st.markdown(
    """
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    .stSidebar {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1f2937;
        color: #f3f4f6;
        border: 1px solid #374151;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "utilizador_atual" not in st.session_state:
    st.session_state.utilizador_atual = "Administrador"
if "cargo_atual" not in st.session_state:
    st.session_state.cargo_atual = "Administrador"
if "fluxo_registo" not in st.session_state:
    st.session_state.fluxo_registo = "login"
if "registo_temp" not in st.session_state:
    st.session_state.registo_temp = {}
if "codigo_gerado" not in st.session_state:
    st.session_state.codigo_gerado = None

if "utilizadores" not in st.session_state:
    senha_hash_padrao = hashlib.sha256("evolution2026".encode()).hexdigest()
    st.session_state.utilizadores = {
        "admin@evolution.com": {
            "nome": "Administrador",
            "senha": senha_hash_padrao,
            "cargo": "Administrador",
        }
    }

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame(
        {
            "Nome": [
                "Tech Solutions Lda",
                "Inovação Digital",
                "Comércio Global",
                "SoftCorp SA",
            ],
            "E-mail": [
                "contacto@techsolutions.com",
                "suporte@inovacao.com",
                "geral@comercioglobal.com",
                "admin@softcorp.com",
            ],
            "Telefone": [
                "+351 912 345 678",
                "+351 923 456 789",
                "+351 934 567 890",
                "+351 965 789 123",
            ],
            "CPF/CNPJ": [
                "12.345.678/0001-90",
                "98.765.432/0001-12",
                "45.678.123/0001-45",
                "78.901.234/0001-67",
            ],
            "Cidade": ["Lisboa", "Porto", "Coimbra", "Braga"],
            "Data de Cadastro": [
                "2026-01-15",
                "2026-02-10",
                "2026-03-01",
                "2026-03-12",
            ],
        }
    )

if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(
        {
            "Nome": [
                "Sistema ERP (Licença)",
                "Notebook Pro",
                "Celular Enterprise",
                "Fone Bluetooth",
                "Consultoria Técnica",
            ],
            "Categoria": [
                "Software",
                "Hardware",
                "Hardware",
                "Acessórios",
                "Serviços",
            ],
            "Preço": [1500.00, 4500.00, 2500.00, 350.00, 800.00],
            "Estoque": [50, 12, 4, 30, 100],
            "Status": [
                "🟢 Disponível",
                "🟢 Disponível",
                "🟡 Estoque baixo",
                "🟢 Disponível",
                "🟢 Disponível",
            ],
        }
    )

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        {
            "Data": [
                "2026-03-01",
                "2026-03-05",
                "2026-03-10",
                "2026-03-14",
            ],
            "Cliente": [
                "Tech Solutions Lda",
                "Inovação Digital",
                "Comércio Global",
                "SoftCorp SA",
            ],
            "Vendedor": ["Ana", "Bruno", "Carla", "Ana"],
            "Produto": [
                "Sistema ERP (Licença)",
                "Notebook Pro",
                "Celular Enterprise",
                "Consultoria Técnica",
            ],
            "Quantidade": [2, 1, 3, 5],
            "Valor Unitário": [1500.00, 4500.00, 2500.00, 800.00],
            "Valor Total": [3000.00, 4500.00, 7500.00, 4000.00],
            "Status": ["Concluída", "Concluída", "Concluída", "Concluída"],
        }
    )


# --- 4. FUNÇÃO DE ENVIO DE E-MAIL REAL VIA SMTP (SECRETS) ---
def enviar_email_real(destinatario, codigo):
    try:
        remetente = (
            st.secrets["smtp"]["email"]
            if "smtp" in st.secrets
            else "evolutiongestaotecnologia@gmail.com"
        )
        senha = st.secrets["smtp"]["password"] if "smtp" in st.secrets else ""

        if not senha:
            # Fallback seguro para testes locais se secrets não estiver preenchido
            return True

        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = "Evolution Gestão Online - Código de Verificação"

        corpo = f"""
        Olá,
        
        O seu código de verificação seguro para concluir o registo no Evolution Gestão Online é: {codigo}
        
        Insira este código de 6 dígitos na plataforma.
        
        Atentamente,
        Equipa Evolution Gestão Tecnologia
        """
        msg.attach(MIMEText(corpo, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


def validar_forca_senha(senha):
    if len(senha) < 8:
        return "Muito fraca (Mínimo de 8 caracteres)"
    tem_numero = any(c.isdigit() for c in senha)
    tem_minuscula = any(c.islower() for c in senha)
    tem_maiuscula = any(c.isupper() for c in senha)
    if len(senha) >= 15:
        return "Forte"
    elif tem_numero and tem_minuscula and tem_maiuscula and len(senha) >= 10:
        return "Muito forte"
    elif tem_numero and tem_minuscula:
        return "Média"
    else:
        return "Fraca"


# --- 5. TELA DE AUTENTICAÇÃO E REGISTO COM FLUXO EXATO ---
def render_auth():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align: center; color: #3b82f6;'>EVOLUTION</h1>",
            unsafe_
