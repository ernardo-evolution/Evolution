# Garantir que a variável do e-mail existe na sessão
        if "email_input" not in st.session_state:
            st.session_state["email_input"] = ""

        st.markdown("### Acesso Direto ao Sistema")
        with st.form("form_login"):
            email = st.text_input("E-mail corporativo", value=st.session_state["email_input"]).strip().lower()
            senha = st.text_input("Palavra-passe", type="password")
            lembrar = st.checkbox("Lembrar de mim neste dispositivo")
            entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if entrar:
                st.session_state["email_input"] = email  # Guarda o e-mail na sessão
                if email and senha:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, nivel, senha, email FROM usuarios WHERE email = ?", (email,))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user and user[2] == gerar_hash_senha(senha):
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_atual"] = user[0]
                        st.session_state["nivel_acesso"] = user[1]
                        st.session_state["email_atual"] = user[3]
                        
                        if lembrar:
                            st.query_params["email"] = user[3]
                            
                        st.success("Sessão iniciada com sucesso!")
                        st.rerun()
                    else:
                        st.error("E-mail ou palavra-passe incorretos.")
                else:
                    st.warning("Preencha todos os campos.")
