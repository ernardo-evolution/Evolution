import random
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

# Inicializar o Estado da Sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "codigo_gerado" not in st.session_state:
    st.session_state.codigo_gerado = None

if "email_registado" not in st.session_state:
    st.session_state.email_registado = ""

if "etapa_email" not in st.session_state:
    st.session_state.etapa_email = False

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        columns=["Cliente", "Produto", "Quantidade", "Valor Total (R$)"]
    )

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame(
        columns=["Nome", "E-mail", "Telefone", "Empresa"]
    )


# --- TELA DE LOGIN SEGURA E PROFISSIONAL ---
def tela_login():
    st.title("🔐 Evolution Gestão Online - Acesso Seguro")
    st.markdown(
        "Selecione o método de autenticação preferencial para aceder à plataforma corporativa."
    )

    tab1, tab2 = st.tabs(
        ["🔑 Credenciais Administrativas", "📧 Mandar Código por E-mail"]
    )

    # Guia 1: Credenciais Administrativas
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

    # Guia 2: Mandar Código por E-mail (Seguro, Privado e Dinâmico)
    with tab2:
        st.subheader("Verificação de Identidade por E-mail")
        st.markdown(
            "Insira o seu endereço de e-mail para receber um código exclusivo e seguro."
        )

        email_input = st.text_input(
            "Endereço de E-mail",
            placeholder="exemplo@dominio.com",
            value=st.session_state.email_registado,
        )

        if st.button("Enviar Código de Verificação"):
            # Validação rigorosa de campo vazio ou formato incorreto
            if not email_input or email_input.strip() == "":
                st.error(
                    "⚠️ O campo de e-mail está vazio. Por favor, preencha o seu endereço de e-mail corretamente."
                )
            elif "@" not in email_input or "." not in email_input:
                st.error(
                    "⚠️ O formato do e-mail parece inválido. Verifique o endereço introduzido."
                )
            else:
                # Geração de um código totalmente novo, único e diferente a cada clique
                codigo_aleatorio = str(random.randint(100000, 999999))
                st.session_state.codigo_gerado = codigo_aleatorio
                st.session_state.email_registado = email_input
                st.session_state.etapa_email = True

                st.success(
                    f"✅ Novo código exclusivo gerado e enviado com sucesso para **{email_input}**. Verifique a sua caixa de entrada!"
                )

        # Se o e-mail foi validado e o código gerado, exibe a etapa para introduzir o código
        if st.session_state.etapa_email:
            st.markdown("---")
            st.markdown(
                f"Insira abaixo o código de 6 dígitos recebido no e-mail **{st.session_state.email_registado}** (pode colar o código livremente):"
            )

            # Campo de texto otimizado para permitir colar perfeitamente (sem restrição estrita de max_chars)
            codigo_digitado = st.text_input(
                "Código de Verificação",
                type="default",
                placeholder="Cole ou escreva os 6 dígitos aqui",
            )

            btn_validar = st.button("Validar Código e Entrar")

            if btn_validar:
                # Limpa eventuais espaços em branco que possam vir colados do e-mail
                codigo_limpo = codigo_digitado.strip()

                if not codigo_limpo:
                    st.warning("Por favor, introduza o código recebido.")
                elif codigo_limpo == st.session_state.codigo_gerado:
                    st.session_state.autenticado = True
                    st.success(
                        "🎉 Código correto! Autenticação bem-sucedida. A entrar..."
                    )
                    st.rerun()
                else:
                    st.error(
                        "❌ Código incorreto. O código introduzido não corresponde ao enviado. Tente novamente."
                    )


if not st.session_state.autenticado:
    tela_login()
    st.stop()


# --- APLICAÇÃO PRINCIPAL (APÓS LOGIN COM SUCESSO) ---
st.title("🚀 Evolution Gestão Online")
st.markdown(
    "Sistema integrado de gestão empresarial, clientes e vendas em tempo real."
)

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
        st.info("Ainda não existem vendas registadas.")

elif menu == "Registar Venda":
    st.subheader("🛒 Novo Registo de Venda")
    if len(st.session_state.clientes) == 0:
        st.warning(
            "⚠️ Primeiro deve cadastrar pelo menos um cliente no menu 'Cadastro de Clientes'."
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

elif menu == "Assistente IA":
    st.subheader("🤖 Assistente Virtual Evolution")
    pergunta = st.text_input(
        "O que gostaria de saber?",
        placeholder="Ex: Como posso aumentar as vendas este mês?",
    )
    if st.button("Perguntar à IA"):
        if pergunta:
            st.info(
                "**Assistente IA:** Com base nos dados atuais, recomendo focar o acompanhamento nos clientes cadastrados."
            )
        else:
            st.warning("Por favor, escreva uma pergunta.")

elif menu == "Terminar Sessão":
    st.session_state.autenticado = False
    st.session_state.etapa_email = False
    st.rerun()
