import streamlit as st
import random
import requests

# Configuração da página
st.set_page_config(
    page_title="A Evolution Gestão Online",
    page_icon="🚀",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #2c5e2e;
        color: white;
        border-radius: 6px;
        height: 45px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1e3f20;
        color: white;
    }
    h1 {
        color: #111;
        font-family: sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estados da sessão (Estado limpo por padrão)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "step" not in st.session_state:
    st.session_state.step = "signup"
if "verification_code" not in st.session_state:
    st.session_state.verification_code = None
if "temp_user_data" not in st.session_state:
    st.session_state.temp_user_data = {}
if "clients" not in st.session_state:
    st.session_state.clients = []
if "products" not in st.session_state:
    st.session_state.products = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente de IA de A Evolution Gestão Online. Como posso ajudar a otimizar o seu negócio hoje?"}
    ]

# --- FUNÇÃO DE ENVIO DE E-MAIL COM DEBUG ---
def send_emailjs_code(to_email, code):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": "service_15qkad9",
        "template_id": "template_mm4esan",
        "user_id": "PCUYqPfeqGQMvHbaD",
        "accessToken": "Mt1w97IKOc8mG4pbR7AAU",
        "template_params": {
            "to_email": to_email,
            "codigo": code
        }
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# --- TELA DE REGISTO / LOGIN ---
if not st.session_state.logged_in:
    
    if st.session_state.step == "signup":
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("<h1>Começar Agora</h1>", unsafe_allow_html=True)
            st.write("Crie a sua conta para aceder a A Evolution Gestão Online.")
            
            with st.form("signup_form"):
                name = st.text_input("Nome", placeholder="Introduza o seu nome")
                email = st.text_input("Endereço de e-mail", placeholder="Introduza o seu e-mail")
                password = st.text_input("Palavra-passe", type="password", placeholder="Palavra-passe")
                terms = st.checkbox("Concordo com os termos e políticas")
                
                submitted = st.form_submit_button("Registar")
                
                if submitted:
                    if not name or not email or not password:
                        st.error("Por favor, preencha todos os campos.")
                    elif not terms:
                        st.error("Deve aceitar os termos e políticas.")
                    else:
                        code = str(random.randint(100000, 999999))
                        st.session_state.verification_code = code
                        st.session_state.temp_user_data = {"name": name, "email": email}
                        
                        with st.spinner("A enviar código de verificação por e-mail... 🚀💨"):
                            status_code, response_text = send_emailjs_code(email, code)
                            
                        if status_code == 200:
                            st.success(f"E-mail enviado com sucesso para {email}!")
                            st.session_state.step = "verify"
                            st.rerun()
                        else:
                            st.error(f"Erro ao enviar o e-mail (Código {status_code}): {response_text}")

            st.write("Já tem uma conta? **Entrar**")
            
        with col2:
            st.image(
                "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80", 
                use_container_width=True
            )

    elif st.session_state.step == "verify":
        st.markdown("<h2>Verificação de E-mail 🚀💨</h2>", unsafe_allow_html=True)
        st.write(f"Enviámos um código de verificação de 6 dígitos para o e-mail: **{st.session_state.temp_user_data.get('email')}**")
        
        user_code = st.text_input("Introduza o código de verificação", max_chars=6)
        
        if st
