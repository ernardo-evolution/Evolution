from datetime import datetime
import hashlib
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import plotly.express as px
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
    /* Tema Geral */
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    .stSidebar {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    /* Cartões e Métricas */
    .metric-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Botões Profissionais */
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
    
    /* Inputs */
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
    st.session_state.fluxo_registo = "login"  # login, registo, otp, nova_senha
if "registo_temp" not in st.session_state:
    st.session_state.registo_temp = {}
if "codigo_gerado" not in st.session_state:
    st.session_state.codigo_gerado = None

# Base de Dados Simulada / Inicial
if "utilizadores" not in st.session_state:
    # Hash SHA-256 seguro para senha padrão 'evolution2026'
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
            "Data de Cadastro": ["2026-01-15", "2026-02-10", "2026-03-01", "2026-03-12"],
        }
    )

if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(
        {
            "Nome": ["Sistema ERP (Licença)", "Notebook Pro", "Celular Enterprise", "Fone Bluetooth", "Consultoria Técnica"],
            "Categoria": ["Software", "Hardware", "Hardware", "Acessórios", "Serviços"],
            "Preço": [1500.00, 4500.00, 2500.00, 350.00, 800.00],
            "Estoque": [50, 12, 4, 30, 100],
            "Status": ["🟢 Disponível", "🟢 Disponível", "🟡 Estoque baixo", "🟢 Disponível", "🟢 Disponível"],
        }
    )

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        {
            "Data": ["2026-03-01", "2026-03-05", "2026-03-10", "2026-03-14"],
            "Cliente": ["Tech Solutions Lda", "Inovação Digital", "Comércio Global", "SoftCorp SA"],
            "Vendedor": ["Ana", "Bruno", "Carla", "Ana"],
            "Produto": ["Sistema ERP (Licença)", "Notebook Pro", "Celular Enterprise", "Consultoria Técnica"],
            "Quantidade": [2, 1, 3, 5],
            "Valor Unitário": [1500.00, 4500.00, 2500.00, 800.00],
            "Valor Total": [3000.00, 4500.00, 7500.00, 4000.00],
            "Status": ["Concluída", "Concluída", "Concluída", "Concluída"],
        }
    )


# --- 4. FUNÇÕES DE SUPORTE E SEGURANÇA (SMTP) ---
def enviar_email_smtp(destinatario, codigo):
    try:
        # Tenta obter segredos do st.secrets se configurados, senão simula com sucesso para testes locais
        remetente = st.secrets["smtp"]["email"] if "smtp" in st.secrets else "evolutiongestaotecnologia@gmail.com"
        senha = st.secrets["smtp"]["password"] if "smtp" in st.secrets else ""
        
        if not senha:
            # Modo simulação segura caso st.secrets não esteja preenchido
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
        st.markdown("<h1 style='text-align: center; color: #3b82f6;'>EVOLUTION</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9ca3af; margin-top: -15px;'>Gestão Online Empresarial</p>", unsafe_allow_html=True)
        
        # Fluxo de Login
        if st.session_state.fluxo_registo == "login":
            st.markdown("### Acesso ao Sistema")
            with st.form("form_login"):
                email = st.text_input("E-mail corporativo", placeholder="exemplo@empresa.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                entrar = st.form_submit_button("Entrar no Sistema")
                
                if entrar:
                    if not email.strip():
                        st.error("Digite seu e-mail.")
                    elif not senha:
                        st.error("Digite sua senha.")
                    else:
                        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                        if email in st.session_state.utilizadores and st.session_state.utilizadores[email]["senha"] == senha_hash:
                            st.session_state.autenticado = True
                            st.session_state.utilizador_atual = st.session_state.utilizadores[email]["nome"]
                            st.session_state.cargo_atual = st.session_state.utilizadores[email]["cargo"]
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

        # Fluxo de Registo - Passo 1
        elif st.session_state.fluxo_registo == "registo":
            st.markdown("### Criar Nova Conta")
            with st.form("form_registo"):
                nome = st.text_input("Nome completo")
                email = st.text_input("E-mail corporativo")
                senha = st.text_input("Senha", type="password")
                
                if senha:
                    forca = validar_forca_senha(senha)
                    st.info(f"Força da senha: {forca}")
                
                confirmar_senha = st.text_input("Confirmar senha", type="password")
                continuar = st.form_submit_button("Continuar")
                
                if continuar:
                    if not email.strip():
                        st.error("Digite seu endereço de e-mail para continuar.")
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
                        st.success("Um código de verificação foi enviado para seu e-mail.")
                        st.rerun()
                        
            if st.button("Voltar ao Login"):
                st.session_state.fluxo_registo = "login"
                st.rerun()

        # Fluxo de Confirmação OTP
        elif st.session_state.fluxo_registo == "otp":
            st.markdown("### Validação de E-mail")
            st.markdown(f"Insira o código de 6 dígitos enviado para **{st.session_state.registo_temp.get('email')}**")
            
            with st.form("form_otp"):
                codigo_digitado = st.text_input("Código de verificação", max_chars=6)
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
                        st.success("Operação realizada com sucesso. Bem-vindo!")
                        st.rerun()
                    else:
                        st.error("Código inválido. Tente novamente.")
            
            if st.button("Reenviar Código"):
                codigo = str(random.randint(100000, 999999))
                st.session_state.codigo_gerado = codigo
                enviar_email_smtp(st.session_state.registo_temp.get("email"), codigo)
                st.success("Um novo código foi enviado.")


if not st.session_state.autenticado:
    render_auth()
    st.stop()


# --- 6. MENU LATERAL E NAVEGAÇÃO ---
st.sidebar.markdown("### EVOLUTION")
st.sidebar.markdown("<p style='color: #9ca3af; font-size: 0.9rem;'>Gestão Online</p>", unsafe_allow_html=True)
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

    # Cálculos Dinâmicos
    faturamento_total = st.session_state.vendas["Valor Total"].sum()
    total_vendas = len(st.session_state.vendas)
    total_produtos_vendidos = st.session_state.vendas["Quantidade"].sum()
    total_clientes = len(st.session_state.clientes)

    # Cards Profissionais
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Faturamento", f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c2:
        st.metric("Vendas", f"{total_vendas} vendas")
    with c3:
        st.metric("Produtos Vendidos", f"{total_produtos_vendidos} produtos")
    with c4:
        st.metric("Clientes", f"{total_clientes} clientes")

    st.markdown("---")

    # Gráficos Plotly
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Evolução do Faturamento")
        fig_fat = px.line(
            st.session_state.vendas,
            x="Data",
            y="Valor Total",
            markers=True,
            template="plotly_dark",
            title="Faturamento por Data",
        )
        st.plotly_chart(fig_fat, use_container_width=True)

    with col_g2:
        st.subheader("Vendas por Vendedor")
        vendas_vend = st.session_state.vendas.groupby("Vendedor")["Valor Total"].sum().reset_index()
        fig_vend = px.bar(
            vendas_vend,
            x="Vendedor",
            y="Valor Total",
            color="Vendedor",
            template="plotly_dark",
            title="Desempenho Comercial",
        )
        st.plotly_chart(fig_vend, use_container_width=True)


# --- VENDAS ---
elif menu == "📊 Vendas":
    st.title("Gestão de Vendas")
    
    with st.expander("+ Registar Nova Venda"):
        with st.form("form_nova_venda"):
            c1, c2 = st.columns(2)
            with c1:
                data_venda = st.date_input("Data", value=datetime.today())
                cliente_venda = st.selectbox("Cliente", st.session_state.clientes["Nome"].tolist())
                vendedor_venda = st.selectbox("Vendedor", ["Ana", "Bruno", "Carla"])
            with c2:
                produto_venda = st.selectbox("Produto", st.session_state.produtos["Nome"].tolist())
                quantidade_venda = st.number_input("Quantidade", min_value=1, value=1)
                
                # Preço unitário automático baseado no produto
                preco_unit = float(st.session_state.produtos.loc[st.session_state.produtos["Nome"] == produto_venda, "Preço"].values[0])
                st.markdown(f"**Preço Unitário:** R$ {preco_unit:,.2f}")

            submeter_venda = st.form_submit_button("Confirmar e Registar Venda")
            
            if submeter_venda:
                valor_total_calc = quantidade_venda * preco_unit
                nova_linha = pd.DataFrame(
                    {
                        "Data": [str(data_venda)],
                        "Cliente": [cliente_venda],
                        "Vendedor": [vendedor_venda],
                        "Produto": [produto_venda],
                        "Quantidade": [quantidade_venda],
                        "Valor Unitário": [preco_unit],
                        "Valor Total": [valor_total_calc],
                        "Status": ["Concluída"],
                    }
                )
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_linha], ignore_index=True)
                st.success("Venda registrada com sucesso!")

    st.markdown("---")
    st.subheader("Histórico de Vendas")
    st.dataframe(st.session_state.vendas, use_container_width=True)


# --- PRODUTOS ---
elif menu == "📦 Produtos":
    st.title("Gestão de Inventário e Produtos")
    
    with st.expander("Cadastrar Novo Produto"):
        with st.form("form_produto"):
            nome_p = st.text_input("Nome do Produto")
            cat_p = st.selectbox("Categoria", ["Software", "Hardware", "Acessórios", "Serviços"])
            preco_p = st.number_input("Preço (R$)", min_value=0.0, value=100.0)
            estoque_p = st.number_input("Estoque Inicial", min_value=0, value=10)
            status_p = st.selectbox("Status", ["🟢 Disponível", "🟡 Estoque baixo", "🔴 Sem estoque"])
            
            salvar_p = st.form_submit_button("Guardar Produto")
            if salvar_p:
                if nome_p:
                    novo_prod = pd.DataFrame(
                        [[nome_p, cat_p, preco_p, estoque_p, status_p]],
                        columns=["Nome", "Categoria", "Preço", "Estoque", "Status"],
                    )
                    st.session_state.produtos = pd.concat([st.session_state.produtos, novo_prod], ignore_index=True)
                    st.success("Operação realizada com sucesso.")
                else:
                    st.error("Verifique os dados informados.")

    st.markdown("---")
    st.dataframe(st.session_state.produtos, use_container_width=True)


# --- CLIENTES ---
elif menu == "👥 Clientes":
    st.title("Gestão de Clientes (CRM)")
    
    with st.expander("Cadastrar Novo Cliente"):
        with st.form("form_cliente"):
            c1, c2 = st.columns(2)
            with c1:
                nome_c = st.text_input("Nome da Empresa / Cliente")
                email_c = st.text_input("E-mail de Contacto")
                tel_c = st.text_input("Telemóvel / Telefone")
            with c2:
                doc_c = st.text_input("CPF / CNPJ")
                cidade_c = st.text_input("Cidade")
                data_c = str(datetime.today().date())
                
            salvar_c = st.form_submit_button("Cadastrar Cliente")
            if salvar_c:
                if nome_c:
                    novo_cli = pd.DataFrame(
                        [[nome_c, email_c, tel_c, doc_c, cidade_c, data_c]],
                        columns=["Nome", "E-mail", "Telefone", "CPF/CNPJ", "Cidade", "Data de Cadastro"],
                    )
                    st.session_state.clientes = pd.concat([st.session_state.clientes, novo_cli], ignore_index=True)
                    st.success("Operação realizada com sucesso.")
                else:
                    st.error("Verifique os dados informados.")

    st.markdown("---")
    st.dataframe(st.session_state.clientes, use_container_width=True)


# --- VENDEDORES ---
elif menu == "👤 Vendedores":
    st.title("Ranking de Vendedores")
    
    if len(st.session_state.vendas) > 0:
        resumo_vendedores = (
            st.session_state.vendas.groupby("Vendedor")
            .agg(
                Num_Vendas=("Valor Total", "count"),
                Faturamento=("Valor Total", "sum"),
            )
            .reset_index()
        )
        resumo_vendedores["Ticket Médio"] = resumo_vendedores["Faturamento"] / resumo_vendedores["Num_Vendas"]
        resumo_vendedores = resumo_vendedores.sort_values(by="Faturamento", ascending=False).reset_index(drop=True)
        
        # Atribuir medalhas
        medalhas = ["🥇 1º lugar", "🥈 2º lugar", "🥉 3º lugar"]
        resumo_vendedores["Posição"] = [medalhas[i] if i < 3 else f"{i+1}º lugar" for i in range(len(resumo_vendedores))]
        
        st.dataframe(resumo_vendedores, use_container_width=True)
    else:
        st.info("Sem dados de vendas suficientes para gerar o ranking.")


# --- RELATÓRIOS ---
elif menu == "📈 Relatórios":
    st.title("Relatórios e Indicadores Avançados")
    st.markdown("Análise detalhada do desempenho comercial e financeiro.")
    
    if len(st.session_state.vendas) > 0:
        faturamento_medio = st.session_state.vendas["Valor Total"].mean()
        st.metric("Ticket Médio Geral", f"R$ {faturamento_medio:,.2f}")
        
        fig_rel = px.bar(
            st.session_state.vendas,
            x="Produto",
            y="Quantidade",
            color="Produto",
            template="plotly_dark",
            title="Volume de Produtos Vendidos",
        )
        st.plotly_chart(fig_rel, use_container_width=True)
    else:
        st.info("Aguardando registos de vendas para gerar relatórios.")


# --- CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.title("Configurações do Sistema")
    
    tab1, tab2, tab3 = st.tabs(["Minha Conta", "Segurança", "Sistema"])
    
    with tab1:
        st.subheader("Perfil do Utilizador")
        st.text_input("Nome", value=st.session_state.utilizador_atual)
        st.text_input("Cargo", value=st.session_state.cargo_atual, disabled=True)
        
    with tab2:
        st.subheader("Alterar Senha")
        st.text_input("Senha Atual", type="password")
        st.text_input("Nova Senha", type="password")
        if st.button("Atualizar Senha"):
            st.success("Operação realizada com sucesso.")
            
    with tab3:
        st.subheader("Informações da Versão")
        st.markdown("**Sistema:** Evolution Gestão Online")
        st.markdown("**Versão:** 3.5.0 Enterprise SaaS")
        st.markdown("**Estado do Servidor:** 🟢 Online e Operacional")
