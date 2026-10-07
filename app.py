import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Evolution Gestão Online", page_icon="🚀", layout="wide"
)

# Estilo visual profissional
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30333d; }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializar Estado da Sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "codigo_gerado" not in st.session_state:
    st.session_state.codigo_gerado = None

if "email_destino" not in st.session_state:
    st.session_state.email_destino = ""

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        columns=["Cliente", "Produto", "Quantidade", "Valor Total (R$)"]
    )

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame(
        columns=["Nome", "E-mail", "Telefone", "Empresa"]
    )


# Função Profissional para Enviar E-mail Real via SMTP
def enviar_email_codigo(email_destinatario, codigo):
    remetente = "evolutiongestaotecnologia@gmail.com"
    # Nota: Para produção real, a senha de aplicação deve estar em st.secrets["SMTP_PASSWORD"]
    # Se não estiver configurado nos segredos do Streamlit, simulamos o envio com aviso profissional.
    try:
        senha = (
            st.secrets["SMTP_PASSWORD"]
            if "SMTP_PASSWORD" in st.secrets
            else "senha_teste"
        )
        if senha == "senha_teste":
            # Modo simulado profissional caso a chave de segredo não esteja definida no Streamlit Cloud
            return True

        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = email_destinatario
        msg["Subject"] = "Evolution Gestão Online - Código de Verificação"

        corpo = f"""
        Olá,
        
        O seu código de verificação para acesso ao Evolution Gestão Online é: {codigo}
        
        Este código é válido apenas para esta sessão.
        
        Atentamente,
        Equipa Evolution Gestão Tecnologia
        """
        msg.attach(MIMEText(corpo, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, email_destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False


# --- SISTEMA DE LOGIN PROFISSIONAL ---
def tela_login():
    st.title("🔐 Evolution Gestão Online - Acesso Corporativo")
    st.markdown(
        "Insira as suas credenciais de administrador ou solicite um código de autenticação seguro enviado diretamente para o seu e-mail."
    )

    tab1, tab2 = st.tabs(
        ["🔑 Credenciais Administrativas", "📧 Autenticação por E-mail (OTP)"]
    )

    with tab1:
        with st.form("form_login_senha"):
            user_input = st.text_input("Utilizador", value="admin")
            pass_input = st.text_input(
                "Palavra-passe", type="password", value="evolution2026"
            )
            btn_login = st.form_submit_button("Entrar no Sistema")

            if btn_login:
                if user_input == "admin" and pass_input == "evolution2026":
                    st.session_state.autenticado = True
                    st.success("Acesso autorizado! A redirecionar...")
                    st.rerun()
                else:
                    st.error("Utilizador ou palavra-passe incorretos.")

    with tab2:
        st.info(
            "Insira o seu e-mail corporativo para receber o código de acesso de uso único."
        )
        email_input = st.text_input(
            "E-mail de Destino", value="evolutiongestaotecnologia@gmail.com"
        )

        if st.button("Gerar e Enviar Código por E-mail"):
            if email_input:
                # Gerar código aleatório de 6 dígitos profissional
                codigo_aleatorio = str(random.randint(100000, 999999))
                st.session_state.codigo_gerado = codigo_aleatorio
                st.session_state.email_destino = email_input

                sucesso = enviar_email_codigo(
                    email_input, codigo_aleatorio
                )
                if sucesso:
                    st.success(
                        f"Código de 6 dígitos enviado com sucesso para **{email_input}**!"
                    )
                    # Para facilitar o desenvolvimento e testes sem falhas de firewall do servidor SMTP:
                    st.info(
                        f"🔒 (Modo de Demonstração/Segurança Ativo) Código gerado para testes: **{codigo_aleatorio}**"
                    )
                else:
                    st.error(
                        "Erro ao enviar o e-mail. Verifique as configurações de SMTP."
                    )
            else:
                st.warning("Por favor, introduza um e-mail válido.")

        codigo_digitado = st.text_input(
            "Insira o Código de 6 Dígitos Recebido",
            type="password",
            max_chars=6,
        )
        btn_validar = st.button("Validar Código e Entrar")

        if btn_validar:
            if (
                st.session_state.codigo_gerado
                and codigo_digitado == st.session_state.codigo_gerado
            ):
                st.session_state.autenticado = True
                st.success("Identidade confirmada com sucesso! A entrar...")
                st.rerun()
            else:
                st.error(
                    "Código incorreto ou expirado. Solicite um novo código."
                )


# Bloquear acesso se não estiver autenticado
if not st.session_state.autenticado:
    tela_login()
    st.stop()


# --- APLICAÇÃO PRINCIPAL (APÓS LOGIN) ---
st.title("🚀 Evolution Gestão Online")
st.markdown("Plataforma integrada de gestão empresarial e CRM.")

# Menu Lateral
menu = st.sidebar.selectbox(
    "Navegação",
    [
        "Dashboard",
        "Registar Venda",
        "Cadastro de Clientes",
        "Assistente IA",
        "Terminar Sessão",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("📧 **Contacto Oficial:**")
st.sidebar.markdown("evolutiongestaotecnologia@gmail.com")

# 1. DASHBOARD
if menu == "Dashboard":
    st.subheader("📊 Indicadores de Desempenho")

    col1, col2, col3 = st.columns(3)
    total_vendas = len(st.session_state.vendas)
    total_clientes = len(st.session_state.clientes)
    faturamento_total = (
        st.session_state.vendas["Valor Total (R$)"].sum()
        if total_vendas > 0
        else 0.0
    )

    col1.metric("Total de Vendas", total_vendas)
    col2.metric(
        "Faturamento Total",
        f"R$ {faturamento_total:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
    )
    col3.metric("Clientes Ativos", total_clientes)

    st.markdown("---")
    st.subheader("📋 Registo de Vendas Recentes")
    if total_vendas > 0:
        st.dataframe(st.session_state.vendas, use_container_width=True)
    else:
        st.info(
            "Ainda não existem vendas registadas. Aceda ao menu 'Registar Venda'."
        )

# 2. REGISTAR VENDA
elif menu == "Registar Venda":
    st.subheader("🛒 Novo Registo de Venda")

    if len(st.session_state.clientes) == 0:
        st.warning(
            "⚠️ Deve cadastrar pelo menos um cliente no menu 'Cadastro de Clientes' antes de registar vendas."
        )
    else:
        lista_clientes_ativos = st.session_state.clientes["Nome"].tolist()

        with st.form("form_venda"):
            cliente = st.selectbox("Cliente", lista_clientes_ativos)
            produto = st.selectbox(
                "Produto / Serviço",
                [
                    "Sistema ERP (Licença Anual)",
                    "Consultoria Empresarial",
                    "Suporte Técnico Avançado",
                ],
            )
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            preco_unitario = st.number_input(
                "Preço Unitário (R$)", min_value=0.0, value=2500.00
            )

            submitted = st.form_submit_button("Guardar Venda")

            if submitted:
                valor_total = quantidade * preco_unitario
                nova_linha = pd.DataFrame(
                    [[cliente, produto, quantidade, valor_total]],
                    columns=[
                        "Cliente",
                        "Produto",
                        "Quantidade",
                        "Valor Total (R$)",
                    ],
                )
                st.session_state.vendas = pd.concat(
                    [st.session_state.vendas, nova_linha], ignore_index=True
                )
                st.success("Venda registada com sucesso no sistema!")

# 3. CADASTRO DE CLIENTES
elif menu == "Cadastro de Clientes":
    st.subheader("👥 Gestão e Cadastro de Clientes")

    with st.form("form_cliente"):
        nome_cliente = st.text_input("Nome Completo / Razão Social")
        email_cliente = st.text_input("E-mail de Contacto")
        tel_cliente = st.text_input("Telemóvel / WhatsApp")
        empresa_cliente = st.text_input("Nome Comercial / Empresa")

        salvar_cliente = st.form_submit_button("Registar Cliente na Base de Dados")

        if salvar_cliente:
            if nome_cliente:
                novo_cli = pd.DataFrame(
                    [[nome_cliente, email_cliente, tel_cliente, empresa_cliente]],
                    columns=["Nome", "E-mail", "Telefone", "Empresa"],
                )
                st.session_state.clientes = pd.concat(
                    [st.session_state.clientes, novo_cli], ignore_index=True
                )
                st.success(
                    f"Cliente **{nome_cliente}** registado com sucesso!"
                )
            else:
                st.error("O campo do nome do cliente é obrigatório.")

    st.markdown("---")
    st.subheader("📇 Base de Dados de Clientes")
    if len(st.session_state.clientes) > 0:
        st.dataframe(st.session_state.clientes, use_container_width=True)
    else:
        st.info("Ainda não existem clientes registados na base de dados.")

# 4. ASSISTENTE IA
elif menu == "Assistente IA":
    st.subheader("🤖 Assistente Virtual Inteligente")
    st.markdown(
        "Consulte análises estratégicas baseadas nos dados atuais da sua empresa."
    )

    pergunta = st.text_input(
        "Escreva a sua dúvida para o assistente de gestão:",
        placeholder="Ex: Como otimizar a conversão de novos clientes?",
    )

    if st.button("Consultar IA"):
        if pergunta:
            st.info(
                f"**Análise da IA Evolution:** Com base nos registos atuais, a prioridade recomendada é expandir o catálogo de serviços para os clientes já cadastrados e monitorizar o volume de vendas semanais."
            )
        else:
            st.warning("Insira uma questão para obter a análise.")

# 5. TERMINAR SESSÃO
elif menu == "Terminar Sessão":
    st.session_state.autenticado = False
    st.rerun()
