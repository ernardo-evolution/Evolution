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

# Título Principal
st.title("🚀 Evolution Gestão Online")
st.markdown("Sistema integrado de gestão empresarial e vendas.")

# Inicializar dados na sessão se não existirem
if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        columns=["Cliente", "Produto", "Quantidade", "Valor Total (R$)"]
    )

# Menu Lateral Simples
menu = st.sidebar.selectbox(
    "Navegação", ["Dashboard", "Registar Venda", "Assistente IA"]
)

# Rodapé da Barra Lateral com o e-mail da empresa
st.sidebar.markdown("---")
st.sidebar.markdown("📧 **Contacto:**")
st.sidebar.markdown("evolutiongestaotecnologia@gmail.com")

# 1. DASHBOARD
if menu == "Dashboard":
    st.subheader("📊 Indicadores de Desempenho")

    col1, col2, col3 = st.columns(3)
    total_vendas = len(st.session_state.vendas)
    faturamento_total = (
        st.session_state.vendas["Valor Total (R$)"].sum()
        if total_vendas > 0
        else 0.0
    )

    col1.metric("Total de Vendas", total_vendas)
    col2.metric(
        "Faturamento Total", f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col3.metric("Clientes Ativos", "3")

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

    with st.form("form_venda"):
        cliente = st.text_input("Nome do Cliente", "Ex: Empresa XPTO")
        produto = st.selectbox(
            "Produto",
            ["Sistema ERP (Licença)", "Consultoria", "Suporte Avançado"],
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
                columns=["Cliente", "Produto", "Quantidade", "Valor Total (R$)"],
            )
            st.session_state.vendas = pd.concat(
                [st.session_state.vendas, nova_linha], ignore_index=True
            )
            st.success("Venda registada com sucesso!")

# 3. ASSISTENTE IA
elif menu == "Assistente IA":
    st.subheader("🤖 Assistente Virtual Evolution")
    st.markdown(
        "Faz perguntas sobre a gestão, finanças ou dicas de vendas do sistema."
    )

    pergunta = st.text_input(
        "O que gostarias de saber?",
        placeholder="Ex: Como posso aumentar as vendas este mês?",
    )

    if st.button("Perguntar à IA"):
        if pergunta:
            st.info(
                f"**Assistente IA:** Com base nos dados atuais do Evolution Gestão Online, recomendo focar o acompanhamento nos clientes mais ativos e otimizar o catálogo de produtos para acelerar o fecho de novas faturas."
            )
        else:
            st.warning("Por favor, escreve uma pergunta para o assistente.")
