import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Evolution Gestão Online", page_icon="🚀", layout="wide"
)

# Estilo visual limpo
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30333d; }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializar Base de Dados na Sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "codigo_enviado" not in st.session_state:
    st.session_state.codigo_enviado = "1234"  # Código padrão de teste

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        columns=["Cliente", "Produto", "Quantidade", "Valor Total (R$)"]
    )

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame(
        columns=["Nome", "E-mail", "Telefone", "Empresa"]
    )


# --- SISTEMA DE LOGIN COM VERIFICAÇÃO POR E-MAIL ---
def tela_login():
    st.title("🔐 Evolution Gestão Online - Acesso Seguro")
    st.markdown(
        "Para entrar no sistema, insira as credenciais e valide o código de acesso enviado para o e-mail da empresa."
    )

    tab1, tab2 = st.tabs(["🔑 Login com Senha", "📧 Entrar com Código por E-mail"])

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
                    st.success("Login efetuado com sucesso! A carregar...")
                    st.rerun()
                else:
                    st.error("Utilizador ou palavra-passe incorretos.")

    with tab2:
        st.info(
            "O código de verificação é enviado para: **evolutiongestaotecnologia@gmail.com**"
        )
        email_input = st.text_input(
            "Confirme o E-mail de Acesso",
            value="evolutiongestaotecnologia@gmail.com",
        )

        if st.button("Enviar Código por E-mail"):
            st.success(
                "Código de verificação simulado enviado com sucesso para o e-mail!"
            )
            st.info(
                "💡 **Dica de teste:** O seu código de acesso atual é **1234**"
            )

        codigo_digitado = st.text_input(
            "Insira o Código de 4 Dígitos Recebido", type="password"
        )
        btn_validar = st.button("Validar Código e Entrar")

        if btn_validar:
            if codigo_digitado == st.session_state.codigo_enviado:
                st.session_state.autenticado = True
                st.success("Código validado com sucesso! A entrar...")
                st.rerun()
            else:
                st.error("Código incorreto. Tente novamente.")


# Se não estiver autenticado, mostra exclusivamente a tela de login e pára aqui
if not st.session_state.autenticado:
    tela_login()
    st.stop()


# --- APLICAÇÃO PRINCIPAL (APÓS LOGIN COM SUCESSO) ---

# Título Principal
st.title("🚀 Evolution Gestão Online")
st.markdown(
    "Sistema integrado de gestão empresarial, clientes e vendas em tempo real."
)

# Menu Lateral de Navegação
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

# Rodapé da Barra Lateral com o e-mail da empresa
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
    col3.metric("Clientes Cadastrados", total_clientes)

    st.markdown("---")
    st.subheader("📋 Registo de Vendas Recentes")
    if total_vendas > 0:
        st.dataframe(st.session_state.vendas, use_container_width=True)
    else:
        st.info(
            "Ainda não existem vendas registadas. Vai ao menu 'Registar Venda' para começar!"
        )

# 2. REGISTAR VENDA
elif menu == "Registar Venda":
    st.subheader("🛒 Novo Registo de Venda")

    if len(st.session_state.clientes) == 0:
        st.warning(
            "⚠️ Primeiro deves cadastrar pelo menos um cliente no menu 'Cadastro de Clientes'."
        )
    else:
        lista_clientes_ativos = st.session_state.clientes["Nome"].tolist()

        with st.form("form_venda"):
            cliente = st.selectbox("Selecionar Cliente", lista_clientes_ativos)
            produto = st.selectbox(
                "Produto",
                [
                    "Sistema ERP (Licença)",
                    "Consultoria",
                    "Suporte Avançado",
                ],
            )
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            preco_unitario = st.number_input(
                "Preço Unitário (R$)", min_value=0.0, value=1500.00
            )

            submitted = st.form_submit_button("Confirmar e Registar Venda")

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
                st.success("Venda registada com sucesso!")

# 3. CADASTRO DE CLIENTES
elif menu == "Cadastro de Clientes":
    st.subheader("👥 Gestão e Cadastro de Clientes")

    with st.form("form_cliente"):
        nome_cliente = st.text_input("Nome do Cliente / Responsável")
        email_cliente = st.text_input("E-mail de Contacto")
        tel_cliente = st.text_input("Telemóvel / Telefone")
        empresa_cliente = st.text_input("Nome da Empresa")

        salvar_cliente = st.form_submit_button("Guardar Novo Cliente")

        if salvar_cliente:
            if nome_cliente:
                novo_cli = pd.DataFrame(
                    [[nome_cliente, email_cliente, tel_cliente, empresa_cliente]],
                    columns=["Nome", "E-mail", "Telefone", "Empresa"],
                )
                st.session_state.clientes = pd.concat(
                    [st.session_state.clientes, novo_cli], ignore_index=True
                )
                st.success(f"Cliente '{nome_cliente}' cadastrado com sucesso!")
            else:
                st.error("O campo do nome é obrigatório.")

    st.markdown("---")
    st.subheader("📇 Lista de Clientes Registados")
    if len(st.session_state.clientes) > 0:
        st.dataframe(st.session_state.clientes, use_container_width=True)
    else:
        st.info("Ainda não existem clientes cadastrados.")

# 4. ASSISTENTE IA
elif menu == "Assistente IA":
    st.subheader("🤖 Assistente Virtual Evolution")
    st.markdown(
        "Faça perguntas sobre a gestão, finanças ou estratégias para o seu negócio."
    )

    pergunta = st.text_input(
        "O que gostaria de saber?",
        placeholder="Ex: Como posso aumentar as vendas este mês?",
    )

    if st.button("Perguntar à IA"):
        if pergunta:
            st.info(
                f"**Assistente IA:** Com base nos dados atuais do Evolution Gestão Online, recomendo focar o acompanhamento nos clientes cadastrados e otimizar o catálogo de produtos para acelerar o fecho de novas faturas."
            )
        else:
            st.warning("Por favor, escreva uma pergunta para o assistente.")

# 5. TERMINAR SESSÃO
elif menu == "Terminar Sessão":
    st.session_state.autenticado = False
    st.rerun()
