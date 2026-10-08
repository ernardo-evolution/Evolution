import random
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Evolution Gestão Online", page_icon="🛡️", layout="centered"
)

# --- GESTÃO DE ESTADO DA SESSÃO ---
if "etapa" not in st.session_state:
  st.session_state.etapa = "capa"

if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = None

if "email_usuario" not in st.session_state:
  st.session_state.email_usuario = ""


# --- ETAPA 1: CAPA ---
if st.session_state.etapa == "capa":
  st.title("🛡️ Evolution Gestão Online")
  st.subheader("Enterprise SaaS Platform (v3.8.1)")
  st.write(
      "Bem-vindo ao sistema de gestão de alta performance. Clique no botão"
      " abaixo para iniciar o seu registo seguro."
  )

  if st.button("Iniciar Registo"):
    st.session_state.etapa = "registo"
    st.rerun()


# --- ETAPA 2: REGISTO COM VALIDAÇÃO DE IDADE ---
elif st.session_state.etapa == "registo":
  st.title("📝 Registo de Novo Utilizador")

  nome = st.text_input("Nome Completo")
  email = st.text_input("E-mail corporativo ou pessoal")
  idade = st.number_input("Idade", min_value=1, max_value=120, value=18)

  if st.button("Avançar para Verificação"):
    if not nome or not email:
      st.warning("Por favor, preencha todos os campos.")
    elif idade < 18:
      st.error(
          "Erro de Validação: O acesso ao sistema requer idade igual ou"
          " superior a 18 anos."
      )
    else:
      st.session_state.email_usuario = email
      
      # Gerar código de 6 dígitos
      codigo = str(random.randint(100000, 999999))
      st.session_state.codigo_gerado = codigo

      # ⚡ MODO RÁPIDO: Mostra o código diretamente no ecrã
      st.success("Código gerado com sucesso!")
      st.info(f"🔑 **[CÓDIGO DE TESTE]**: {codigo}")

      st.session_state.etapa = "verificacao"
      st.rerun()


# --- ETAPA 3: VALIDAÇÃO DO CÓDIGO DE SEGURANÇA ---
elif st.session_state.etapa == "verificacao":
  st.title("🔒 Validação de Segurança do Sistema")
  st.write(
      f"Insira o código de 6 dígitos enviado para:"
      f" **{st.session_state.email_usuario}**"
  )

  codigo_inserido = st.text_input(
      "Código de verificação", type="default", max_chars=6
  )

  col1, col2 = st.columns(2)

  with col1:
    if st.button("Confirmar Código"):
      if codigo_inserido == st.session_state.codigo_gerado:
        st.success("Autenticação bem-sucedida! A entrar no sistema...")
        st.session_state.etapa = "app_principal"
        st.rerun()
      else:
        st.error("Código incorreto. Tente novamente.")

  with col2:
    if st.button("Gerar Novo Código"):
      novo_codigo = str(random.randint(100000, 999999))
      st.session_state.codigo_gerado = novo_codigo
      st.success("Novo código gerado!")
      st.info(f"🔑 **[CÓDIGO DE TESTE]**: {novo_codigo}")


# --- ETAPA 4: APLICAÇÃO PRINCIPAL ---
elif st.session_state.etapa == "app_principal":
  st.title("🚀 Evolution Gestão Online - Painel Principal")
  st.success("Sessão autenticada com sucesso!")
  st.write(
      "Aqui tens acesso a todas as ferramentas corporativas da v3.8.1."
  )

  if st.button("Terminar Sessão"):
    st.session_state.etapa = "capa"
    st.session_state.codigo_gerado = None
    st.session_state.email_usuario = ""
    st.rerun()
