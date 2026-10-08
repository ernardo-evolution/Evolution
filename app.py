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

# --- 2. DESIGN E CSS PERSONALIZADO (ESTILO SAAS PROFISSIONAL) ---
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


# --- 4. FUNÇÕES DE SUPORTE E SEGURANÇA (SMTP) ---
def enviar_email_smtp(destinatario, codigo):
    try:
        remetente = (
            st.secrets["smtp"]["email"]
            if "smtp" in st.secrets
            else "evolutiongestaotecnologia@gmail.com"
        )
        senha = st.secrets["smtp"]["password"] if "smtp" in st.secrets else ""
        if not senha:
            return True
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = "Evolution Gestão Online - Código de Verificação"
        corpo = f"O seu código de verificação seguro é: {codigo}. Válido por 10 minutos."
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


# --- 5. TELA DE AUTENTICAÇÃO E REGISTO ---
def render_auth():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align: center; color: #3b82f6;'>EVOLUTION</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: #9ca3af; margin-top: -15px;'>Gestão Online Empresarial</p>",
            unsafe_allow_html=True,
        )

        if st.session_state.fluxo_registo == "login":
            st.markdown("### Acesso ao Sistema")
            with st.form("form_login"):
                email = st.text_input(
                    "E-mail corporativo", placeholder="exemplo@empresa.com"
                )
                senha = st.text_input(
                    "Senha", type="password", placeholder="••••••••"
                )
                entrar = st.form_submit_button("Entrar no Sistema")
                if entrar:
                    if not email.strip():
                        st.error("Digite seu e-mail.")
                    elif not senha:
                        st.error("Digite sua senha.")
                    else:
                        senha_hash = hashlib.sha256(
                            senha.encode()
                        ).hexdigest()
                        if (
                            email in st.session_state.utilizadores
                            and st.session_state.utilizadores[email]["senha"]
                            == senha_hash
                        ):
                            st.session_state.autenticado = True
                            st.session_state.utilizador_atual = (
                                st.session_state.utilizadores[email]["nome"]
                            )
                            st.session_state.cargo_atual = (
                                st.session_state.utilizadores[email]["cargo"]
                            )
                            st.success("Login efetuado com sucesso!")
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Criar uma conta"):
                    st.session_state.fluxo_registo = "registo"
                    st.rerun()
            with col_b:
                if st.button("Esqueci minha senha"):
                    st.session_state.fluxo_registo = "recuperar"
                    st.rerun()

        elif st.session_state.fluxo_registo == "registo":
            st.markdown("### Criar Nova Conta")
            with st.form("form_registo"):
                nome = st.text_input("Nome completo")
                email = st.text_input("E-mail corporativo")
                senha = st.text_input("Senha", type="password")
                if senha:
                    forca = validar_forca_senha(senha)
                    st.info(f"Força da senha: {forca}")
                confirmar_senha = st.text_input(
                    "Confirmar senha", type="password"
                )
                continuar = st.form_submit_button("Continuar")
                if continuar:
                    if not email.strip():
                        st.error(
                            "Digite seu endereço de e-mail para continuar."
                        )
                    elif "@" not in email or "." not in email:
                        st.error("Digite um endereço de e-mail válido.")
                    elif senha != confirmar_senha:
                        st.error("As senhas não coincidem.")
                    elif len(senha) < 8:
                        st.error("A senha deve ter pelo menos 8 caracteres.")
                    else:
                        codigo = str(random.randint(100000, 999999))
                        st.session_state.codigo_gerado = codigo
                        st.session_state.registo_temp = {
                            "nome": nome,
                            "email": email,
                            "senha": hashlib.sha256(senha.encode()).hexdigest(),
                        }
                        enviar_email_smtp(email, codigo)
                        st.session_state.fluxo_registo = "otp"
                        st.success(
                            "Um código de verificação foi enviado para seu e-mail."
                        )
                        st.rerun()
            if st.button("Voltar ao Login"):
                st.session_state.fluxo_registo = "login"
                st.rerun()

        elif st.session_state.fluxo_registo == "otp":
            st.markdown("### Validação de E-mail")
            st.markdown(
                f"Insira o código de 6 dígitos enviado para **{st.session_state.registo_temp.get('email')}**"
            )
            with st.form("form_otp"):
                codigo_digitado = st.text_input(
                    "Código de verificação", max_chars=6
                )
                validar = st.form_submit_button("Confirmar Código")
                if validar:
                    if codigo_digitado.strip() == st.session_state.codigo_gerado:
                        novo_user = st.session_state.registo_temp
                        st.session_state.utilizadores[novo_user["email"]] = {
                            "nome": novo_user["nome"],
                            "senha": novo_user["senha"],
                            "cargo": "Gestor",
                        }
                        st.session_state.autenticado = True
                        st.session_state.utilizador_atual = novo_user["nome"]
                        st.session_state.cargo_atual = "Gestor"
                        st.success(
                            "Operação realizada com sucesso. Bem-vindo!"
                        )
                        st.rerun()
                    else:
                        st.error("Código inválido. Tente novamente.")
            if st.button("Reenviar Código"):
                codigo = str(random.randint(100000, 999999))
                st.session_state.codigo_gerado = codigo
                enviar_email_smtp(
                    st.session_state.registo_temp.get("email"), codigo
                )
                st.success("Um novo código foi enviado.")


if not st.session_state.autenticado:
    render_auth()
    st.stop()


# --- 6. MENU LATERAL E NAVEGAÇÃO ---
st.sidebar.markdown("### EVOLUTION")
st.sidebar.markdown(
    "<p style='color: #9ca3af; font-size: 0.9rem;'>Gestão Online</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    [
        "🏠 Dashboard",
        "📊 Vendas",
        "📦 Produtos",
        "👥 Clientes",
        "👤 Vendedores",
        "📈 Relatórios",
        "⚙️ Configurações",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **{st.session_state.utilizador_atual}**")
st.sidebar.markdown(f"🔑 *{st.session_state.cargo_atual}*")

if st.sidebar.button("🚪 Terminar Sessão"):
    st.session_state.autenticado = False
    st.session_state.fluxo_registo = "login"
    st.rerun()


# --- 7. MÓDULOS DA APLICAÇÃO ---

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Dashboard")
    st.markdown("Visão geral da sua gestão em tempo real.")

    faturamento_total = st.session_state.vendas["Valor Total"].sum()
    total_vendas = len(st.session_state.vendas)
    total_produtos_vendidos = st.session_state.vendas["Quantidade"].sum()
    total_clientes = len(st.session_state.clientes)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Faturamento",
            f"R$ {faturamento_total:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )
    with c2:
        st.metric("Vendas", f"{total_vendas} vendas")
    with c3:
        st.metric("Produtos Vendidos", f"{total_produtos_vendidos} produtos")
    with c4:
        st.metric("Clientes", f"{total_clientes} clientes")

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Evolução do Faturamento")
        df_fat = (
            st.session_state.vendas.groupby("Data")["Valor Total"]
            .sum()
            .reset_index()
        )
        st.line_chart(df_fat.set_index("Data"))

    with col_g2:
        st.subheader("Vendas por Vendedor")
        df_vend = (
            st.session_state.vendas.groupby("Vendedor")["Valor Total"]
            .sum()
            .reset_index()
        )
        st.bar_chart(df_vend.set_index("Vendedor"))


# --- VENDAS ---
elif menu == "📊 Vendas":
    st.title("Gestão de Vendas")
    with st.expander("+ Registar Nova Venda"):
        with st.form("form_nova_venda"):
            c1, c2 = st.columns(2)
            with c1:
                data_venda = st.date_input("Data", value=datetime.today())
                cliente_venda = st.selectbox(
                    "Cliente", st.session
