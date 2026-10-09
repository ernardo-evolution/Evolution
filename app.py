import streamlit as st
import random
import requests

# Dicionário de Traduções para os 3 Idiomas
TRANSLATIONS = {
    "Português": {
        "app_title": "A Evolution Gestão Online",
        "nav_dashboard": "Dashboard",
        "nav_clients": "Gestão de Clientes",
        "nav_products": "Gestão de Produtos",
        "nav_ai": "Assistente de IA",
        "nav_logout": "Sair",
        "signup_heading": "Começar Agora",
        "signup_sub": "Crie a sua conta para aceder a A Evolution Gestão Online.",
        "name_label": "Nome",
        "email_label": "Endereço de e-mail",
        "pass_label": "Palavra-passe",
        "terms_label": "Concordo com os termos e políticas",
        "register_btn": "Registar",
        "login_prompt": "Já tem uma conta? **Entrar**",
        "verify_title": "Verificação de E-mail 🚀💨",
        "verify_sub": "Enviámos um código de verificação de 6 dígitos para o e-mail:",
        "verify_input": "Introduza o código de verificação",
        "confirm_btn": "Confirmar Código",
        "resend_btn": "Reenviar Código",
        "total_clients": "Total de Clientes",
        "total_products": "Total de Produtos",
        "clean_state_info": "O sistema iniciou completamente limpo, pronto a registar dados reais.",
        "add_client_title": "👥 Gestão de Clientes",
        "client_name": "Nome do Cliente",
        "client_email": "E-mail do Cliente",
        "add_client_btn": "Adicionar Cliente",
        "client_success": "Cliente adicionado com sucesso!",
        "client_list": "### Lista de Clientes Registados",
        "no_clients": "Ainda não existem clientes registados na base de dados.",
        "add_prod_title": "📦 Gestão de Produtos",
        "prod_name": "Nome do Produto",
        "prod_price": "Preço (€)",
        "prod_stock": "Stock Inicial",
        "add_prod_btn": "Adicionar Produto",
        "prod_success": "Produto adicionado com sucesso!",
        "prod_list": "### Lista de Produtos em Stock",
        "no_prod": "Ainda não existem produtos registados no sistema.",
        "ai_title": "🤖 Assistente de IA - A Evolution",
        "ai_sub": "Converse com o assistente inteligente para obter orientações de negócio.",
        "ai_placeholder": "Escreva a sua questão para a IA...",
        "fill_all": "Por favor, preencha todos os campos.",
        "accept_terms": "Deve aceitar os termos e políticas.",
        "email_sent": "E-mail enviado com sucesso para",
        "verify_success": "E-mail verificado com sucesso! A entrar...",
        "wrong_code": "Código incorreto. Tente novamente."
    },
    "English": {
        "app_title": "A Evolution Online Management",
        "nav_dashboard": "Dashboard",
        "nav_clients": "Client Management",
        "nav_products": "Product Management",
        "nav_ai": "AI Assistant",
        "nav_logout": "Log out",
        "signup_heading": "Get Started",
        "signup_sub": "Create your account to access A Evolution Online Management.",
        "name_label": "Name",
        "email_label": "Email address",
        "pass_label": "Password",
        "terms_label": "I agree to the terms and policies",
        "register_btn": "Register",
        "login_prompt": "Already have an account? **Log in**",
        "verify_title": "Email Verification 🚀💨",
        "verify_sub": "We sent a 6-digit verification code to the email:",
        "verify_input": "Enter verification code",
        "confirm_btn": "Confirm Code",
        "resend_btn": "Resend Code",
        "total_clients": "Total Clients",
        "total_products": "Total Products",
        "clean_state_info": "The system started completely clean, ready to record real data.",
        "add_client_title": "👥 Client Management",
        "client_name": "Client Name",
        "client_email": "Client Email",
        "add_client_btn": "Add Client",
        "client_success": "Client successfully added!",
        "client_list": "### Registered Clients List",
        "no_clients": "There are no clients registered in the database yet.",
        "add_prod_title": "📦 Product Management",
        "prod_name": "Product Name",
        "prod_price": "Price (€)",
        "prod_stock": "Initial Stock",
        "add_prod_btn": "Add Product",
        "prod_success": "Product successfully added!",
        "prod_list": "### Stock Products List",
        "no_prod": "There are no products registered in the system yet.",
        "ai_title": "🤖 AI Assistant - A Evolution",
        "ai_sub": "Chat with the intelligent assistant to get business guidance.",
        "ai_placeholder": "Type your question for the AI...",
        "fill_all": "Please fill in all fields.",
        "accept_terms": "You must accept the terms and policies.",
        "email_sent": "Email successfully sent to",
        "verify_success": "Email verified successfully! Logging in...",
        "wrong_code": "Incorrect code. Try again."
    },
    "Español": {
        "app_title": "A Evolution Gestión Online",
        "nav_dashboard": "Dashboard",
        "nav_clients": "Gestión de Clientes",
        "nav_products": "Gestión de Productos",
        "nav_ai": "Asistente de IA",
        "nav_logout": "Salir",
        "signup_heading": "Empezar Ahora",
        "signup_sub": "Cree su cuenta para acceder a A Evolution Gestión Online.",
        "name_label": "Nombre",
        "email_label": "Correo electrónico",
        "pass_label": "Contraseña",
        "terms_label": "Acepto los términos y políticas",
        "register_btn": "Registrarse",
        "login_prompt": "¿Ya tiene una cuenta? **Entrar**",
        "verify_title": "Verificación de Correo 🚀💨",
        "verify_sub": "Hemos enviado un código de verificación de 6 dígitos al correo:",
        "verify_input": "Introduzca el código de verificación",
        "confirm_btn": "Confirmar Código",
        "resend_btn": "Reenviar Código",
        "total_clients": "Total de Clientes",
        "total_products": "Total de Productos",
        "clean_state_info": "El sistema se inició completamente limpio, listo para registrar datos reales.",
        "add_client_title": "👥 Gestión de Clientes",
        "client_name": "Nombre del Cliente",
        "client_email": "Correo del Cliente",
        "add_client_btn": "Añadir Cliente",
        "client_success": "¡Cliente añadido con éxito!",
        "client_list": "### Lista de Clientes Registrados",
        "no_clients": "Aún no hay clientes registrados en la base de dados.",
        "add_prod_title": "📦 Gestión de Productos",
        "prod_name": "Nombre del Producto",
        "prod_price": "Precio (€)",
        "prod_stock": "Stock Inicial",
        "add_prod_btn": "Añadir Producto",
        "prod_success": "¡Producto añadido con éxito!",
        "prod_list": "### Lista de Productos en Stock",
        "no_prod": "Aún no hay productos registrados en el sistema.",
        "ai_title": "🤖 Asistente de IA - A Evolution",
        "ai_sub": "Chatee con el asistente inteligente para obtener orientación de negocios.",
        "ai_placeholder": "Escriba su pregunta para la IA...",
        "fill_all": "Por favor, complete todos los campos.",
        "accept_terms": "Debe aceptar los términos y políticas.",
        "email_sent": "¡Correo enviado con éxito a",
        "verify_success": "¡Correo verificado con éxito! Entrando...",
        "wrong_code": "Código incorrecto. Inténtelo de nuevo."
    }
}

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

# Inicializar estados da sessão
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
        {"role": "assistant", "content": "Olá! Sou o assistente de IA. Como posso ajudar?"}
    ]

# Seletor de Idioma na barra lateral (Português, English, Español)
st.sidebar.markdown("### 🌐 Idioma / Language / Idioma")
selected_lang = st.sidebar.selectbox("", ["Português", "English", "Español"], label_visibility="collapsed")
t = TRANSLATIONS[selected_lang]

# --- FUNÇÃO DE ENVIO DE E-MAIL (COM MÚLTIPLAS VARIÁVEIS PARA GARANTIR ENTREGA) ---
def send_emailjs_code(to_email, code):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": "service_15qkad9",
        "template_id": "template_mm4esan",
        "user_id": "PCUYqPfeqGQMvHbaD",
        "accessToken": "Mt1w97IKOc8mG4pbR7AAU",
        "template_params": {
            "to_email": to_email,
            "email": to_email,
            "codigo": code,
            "code": code,
            "message": code
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
            st.markdown(f"<h1>{t['signup_heading']}</h1>", unsafe_allow_html=True)
            st.write(t['signup_sub'])
            
            with st.form("signup_form"):
                name = st.text_input(t['name_label'], placeholder="")
                email = st.text_input(t['email_label'], placeholder="")
                password = st.text_input(t['pass_label'], type="password", placeholder="")
                terms = st.checkbox(t['terms_label'])
                
                submitted = st.form_submit_button(t['register_btn'])
                
                if submitted:
                    if not name or not email or not password:
                        st.error(t['fill_all'])
                    elif not terms:
                        st.error(t['accept_terms'])
                    else:
                        code = str(random.randint(100000, 999999))
                        st.session_state.verification_code = code
                        st.session_state.temp_user_data = {"name": name, "email": email}
                        
                        with st.spinner("..."):
                            status_code, response_text = send_emailjs_code(email, code)
                            
                        if status_code == 200:
                            st.success(f"{t['email_sent']} {email}!")
                            st.session_state.step = "verify"
                            st.rerun()
                        else:
                            st.error(f"Erro ({status_code}): {response_text}")

            st.markdown(t['login_prompt'], unsafe_allow_html=True)
            
        with col2:
            st.image(
                "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80", 
                use_container_width=True
            )

    elif st.session_state.step == "verify":
        st.markdown(f"<h2>{t['verify_title']}</h2>", unsafe_allow_html=True)
        st.write(f"{t['verify_sub']} **{st.session_state.temp_user_data.get('email')}**")
        
        user_code = st.text_input(t['verify_input'], max_chars=6)
        
        if st.button(t['confirm_btn']):
            if user_code == st.session_state.verification_code:
                st.success(t['verify_success'])
                st.session_state.logged_in = True
                st.session_state.step = "app"
                st.rerun()
            else:
                st.error(t['wrong_code'])
                
        if st.button(t['resend_btn']):
            code = str(random.randint(100000, 999999))
            st.session_state.verification_code = code
            send_emailjs_code(st.session_state.temp_user_data.get('email'), code)
            st.success("OK!")

# --- APLICAÇÃO PRINCIPAL ---
else:
    st.sidebar.title("A Evolution 🚀")
    st.sidebar.write(f"Utilizador: **{st.session_state.temp_user_data.get('name', 'Admin')}**")
    
    menu = st.sidebar.selectbox("Navegação", [
        t['nav_dashboard'], 
        t['nav_clients'], 
        t['nav_products'], 
        t['nav_ai'], 
        t['nav_logout']
    ])
    
    if menu == t['nav_dashboard']:
        st.title(f"🚀💨 {t['nav_dashboard']} - A Evolution")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(t['total_clients'], len(st.session_state.clients))
        with col_m2:
            st.metric(t['total_products'], len(st.session_state.products))
            
        st.info(t['clean_state_info'])
        
    elif menu == t['nav_clients']:
        st.title(t['add_client_title'])
        
        with st.form("add_client"):
            new_client_name = st.text_input(t['client_name'])
            new_client_email = st.text_input(t['client_email'])
            add_btn = st.form_submit_button(t['add_client_btn'])
            
            if add_btn and new_client_name:
                st.session_state.clients.append({"name": new_client_name, "email": new_client_email})
                st.success(t['client_success'])
                
        if st.session_state.clients:
            st.markdown(t['client_list'])
            for idx, client in enumerate(st.session_state.clients):
                st.write(f"{idx+1}. **{client['name']}** ({client['email']})")
        else:
            st.warning(t['no_clients'])
            
    elif menu == t['nav_products']:
        st.title(t['add_prod_title'])
        
        with st.form("add_product"):
            prod_name = st.text_input(t['prod_name'])
            prod_price = st.number_input(t['prod_price'], min_value=0.0, format="%.2f")
            prod_stock = st.number_input(t['prod_stock'], min_value=0, step=1)
            add_prod_btn = st.form_submit_button(t['add_prod_btn'])
            
            if add_prod_btn and prod_name:
                st.session_state.products.append({"name": prod_name, "price": prod_price, "stock": prod_stock})
                st.success(t['prod_success'])
                
        if st.session_state.products:
            st.markdown(t['prod_list'])
            for idx, prod in enumerate(st.session_state.products):
                st.write(f"{idx+1}. **{prod['name']}** — {prod['price']:.2f}€ | Stock: **{prod['stock']}**")
        else:
            st.warning(t['no_prod'])
            
    elif menu == t['nav_ai']:
        st.title(t['ai_title'])
        st.write(t['ai_sub'])
        
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input(t['ai_placeholder']):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            response = f"Compreendi a sua questão ('{prompt}'). Continue a focar-se na gestão e otimização do seu negócio!"
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
                
    elif menu == t['nav_logout']:
        st.session_state.logged_in = False
        st.session_state.step = "signup"
        st.rerun()
