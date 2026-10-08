import random
import time
import resend
import streamlit as st

# Configura a chave do Resend
try:
  resend.api_key = st.secrets["RESEND_API_KEY"]
except Exception:
  resend.api_key = "coloca_aqui_a_tua_chave_se_necessario"


def enviar_codigo_verificacao(email_destino, codigo):
  """Envia o código de verificação de 6 dígitos utilizando a API do Resend."""
  try:
    params = {
        "from": "Evolution Gestão <onboarding@resend.dev>",
        "to": [email_destino],
        "subject": "Código de Verificação - A Evolution Gestão Online",
        "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafb; border-radius: 8px; max-width: 600px; margin: auto;">
                    <h2 style="color: #1e3a8a; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">A Evolution Gestão Online</h2>
                    <p style="font-size: 16px; color: #374151;">Olá!</p>
                    <p style="font-size: 16px; color: #374151;">O seu código de verificação para acesso seguro é:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: #ffffff; padding: 15px 25px; border-radius: 6px; border-left: 4px solid #2563eb; font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #111827; display: inline-block;">
                            {codigo}
                        </div>
                    </div>
                </div>
            """,
    }
    resend.Emails.send(params)
    return True
  except Exception as e:
    st.error(f"Erro ao enviar e-mail: {e}")
    return False


# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(
    page_title="A Evolution - Gestão Online",
    page_icon="🚀",
    layout="wide",
)

# Inicializar Estados da Sessão
if "etapa" not in st.session_state:
  st.session_state.etapa = "login"
if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = None
if "email_utilizador" not in st.session_state:
  st.session_state.email_utilizador = ""
if "animacao_vista" not in st.session_state:
  st.session_state.animacao_vista = False

# Base de dados em memória para os Clientes (inicia vazia para começares do zero)
if "clientes" not in st.session_state:
  st.session_state.clientes = []


# --- FLUXO DE LOGIN / VERIFICAÇÃO ---
if st.session_state.etapa == "login":
  st.markdown(
      "<h1 style='text-align: center;'>🚀 A Evolution - Gestão Online</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h3 style='text-align: center; color: #64748b;'>Acesso Seguro</h3>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    email_input = st.text_input("E-mail corporativo", value="")

    if st.button("Enviar Código de Verificação", use_container_width=True):
      if email_input:
        codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
        st.session_state.codigo_gerado = codigo
        st.session_state.email_utilizador = email_input

        with st.spinner("A enviar e-mail através do Resend..."):
          sucesso = enviar_codigo_verificacao(email_input, codigo)

        if sucesso:
          st.success("Código enviado! Verifique a sua caixa de entrada.")
          st.session_state.etapa = "verificar"
          st.rerun()
      else:
        st.warning("Por favor, insira um e-mail válido.")

elif st.session_state.etapa == "verificar":
  st.markdown(
      "<h1 style='text-align: center;'>🔐 Verificação de Segurança</h1>",
      unsafe_allow_html=True,
  )
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    st.info(f"Enviámos um código para: **{st.session_state.email_utilizador}**")
    codigo_digitado = st.text_input("Insira o código de 6 dígitos", max_chars=6)

    col_a, col_b = st.columns(2)
    with col_a:
      if st.button("Confirmar Código", use_container_width=True):
        if codigo_digitado == st.session_state.codigo_gerado:
          st.session_state.etapa = "dashboard"
          st.session_state.animacao_vista = False
          st.rerun()
        else:
          st.error("Código incorreto.")

    with col_b:
      if st.button("Reenviar", use_container_width=True):
        codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
        st.session_state.codigo_gerado = codigo
        if enviar_codigo_verificacao(st.session_state.email_utilizador, codigo):
          st.success("Novo código enviado!")

elif st.session_state.etapa == "dashboard":
  # --- ANIMAÇÃO DE LANÇAMENTO DA NAVE (A EVOLUTION) ---
  if not st.session_state.animacao_vista:
    placeholder = st.empty()
    with placeholder.container():
      st.markdown(
          """
            <style>
            @keyframes launch {
                0% { transform: translateY(120px) scale(0.8); opacity: 0; }
                50% { opacity: 1; transform: translateY(0px) scale(1.1); }
                100% { transform: translateY(-80px) scale(1); opacity: 0; }
            }
            .rocket-box {
                text-align: center;
                padding: 60px 20px;
                background: linear-gradient(to bottom, #0f172a, #1e293b);
                border-radius: 12px;
                margin-top: 50px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }
            .rocket-emoji {
                font-size: 90px;
                animation: launch 2.8s ease-in-out forwards;
            }
            .empresa-title {
                text-align: center;
                font-size: 36px;
                font-weight: 800;
                color: #38bdf8;
                margin-top: 20px;
                letter-spacing: 2px;
            }
            .empresa-sub {
                text-align: center;
                font-size: 18px;
                color: #94a3b8;
                margin-top: 5px;
            }
            </style>
            <div class="rocket-box">
                <div class="rocket-emoji">🚀💨</div>
                <div class="empresa-title">A EVOLUTION</div>
                <div class="empresa-sub">A descolar para o sucesso...</div>
            </div>
            """,
          unsafe_allow_html=True,
      )
      time.sleep(3.0)
    placeholder.empty()
    st.session_state.animacao_vista = True
    st.rerun()

  # --- PAINEL PRINCIPAL & GESTÃO DE CLIENTES ---
  st.sidebar.title("📌 Menu Principal")
  menu = st.sidebar.radio(
      "Navegação", ["Dashboard", "Gestão de Clientes", "Terminar Sessão"]
  )

  if menu == "Dashboard":
    st.balloons()
    st.title("🌟 Bem-vindo ao Dashboard - A Evolution")
    st.write("Sistema integrado com sucesso e pronto a operar!")

    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes Registados", len(st.session_state.clientes))
    col2.metric("Estado da API Resend", "Ativo 🟢")
    col3.metric("Versão do Sistema", "v3.8.1")

  elif menu == "Gestão de Clientes":
    st.title("👥 Gestão de Clientes - A Evolution")
    st.write("Consulte, adicione ou gira os clientes da plataforma.")

    # Formulário para adicionar novo cliente
    with st.expander("➕ Adicionar Novo Cliente", expanded=True):
      with st.form("form_cliente"):
        novo_nome = st.text_input("Nome da Empresa / Cliente")
        novo_email = st.text_input("E-mail de Contacto")
        novo_tel = st.text_input("Telefone")
        novo_plano = st.selectbox(
            "Plano", ["Básico", "Profissional", "Enterprise"]
        )

        submeter = st.form_submit_button("Guardar Cliente")
        if submeter:
          if novo_nome and novo_email:
            novo_id = (
                max([c["id"] for c in st.session_state.clientes], default=0) + 1
            )
            st.session_state.clientes.append({
                "id": novo_id,
                "nome": novo_nome,
                "email": novo_email,
                "telefone": novo_tel,
                "plano": novo_plano,
            })
            st.success(f"Cliente '{novo_nome}' adicionado com sucesso!")
            st.rerun()
          else:
            st.warning("Preencha pelo menos o Nome e o E-mail.")

    # Listagem de clientes
    st.subheader("📋 Lista de Clientes Atuais")
    if st.session_state.clientes:
      for cliente in st.session_state.clientes:
        with st.container():
          col_info1, col_info2, col_info3 = st.columns([3, 3, 2])
          col_info1.write(f"**{cliente['nome']}** ({cliente['plano']})")
          col_info2.write(f"📧 {cliente['email']} | 📞 {cliente['telefone']}")

          if col_info3.button(
              "Remover", key=f"del_{cliente['id']}", type="secondary"
          ):
            st.session_state.clientes = [
                c for c in st.session_state.clientes if c["id"] != cliente["id"]
            ]
            st.rerun()
          st.divider()
    else:
      st.info(
          "Ainda não existem clientes registados. Adicione o seu primeiro"
          " cliente acima!"
      )

  elif menu == "Terminar Sessão":
    st.session_state.etapa = "login"
    st.session_state.codigo_gerado = None
    st.session_state.email_utilizador = ""
    st.session_state.animacao_vista = False
    st.rerun()
