elif st.session_state["modo_recuperacao"]:
    st.markdown("### 🔑 Recuperar Acesso / Obter Código Direto")
    st.markdown("Insira o seu e-mail corporativo registado para receber um novo código de verificação imediatamente.")

    with st.form("form_recuperar_acesso"):
      email_rec = st.text_input("E-mail associado à conta").strip().lower()
      col_r1, col_r2 = st.columns(2)
      with col_r1:
        btn_enviar_rec = st.form_submit_button("Enviar Código por E-mail", use_container_width=True)
      with col_r2:
        btn_voltar_login = st.form_submit_button("Voltar ao Login", use_container_width=True)

      rastreamento_id = secrets.token_hex(6)

      if btn_enviar_rec:
        if not email_rec or "@" not in email_rec:
          st.error("Insira um endereço de e-mail válido.")
        else:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute("SELECT id, nome, username FROM usuarios WHERE email = ?", (email_rec,))
          u_data = cursor.fetchone()

          if u_data:
            u_id, u_nome, u_username = u_data
            novo_codigo = f"{random.randint(0, 999999):06d}"
            nova_expiracao = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "UPDATE usuarios SET codigo_verificacao = ?, codigo_expiracao = ?, tentativas_codigo = 0 WHERE id = ?",
                (novo_codigo, nova_expiracao, u_id)
            )
            conn.commit()
            conn.close()

            registrar_historico_profissional(u_nome, u_username, email_rec, "Recuperação de Acesso", "Solicitação de envio direto de código", "Pendente", "EmailJS", "", rastreamento_id)
            sucesso_ej, msg_ej = disparar_emailjs(email_rec, u_nome, novo_codigo, rastreamento_id)

            if sucesso_ej:
              st.session_state["aguardando_verificacao"] = email_rec
              st.session_state["modo_recuperacao"] = False
              st.success("Código de verificação enviado com sucesso para o seu e-mail via EmailJS!")
              st.rerun()
            else:
              st.error(f"Erro ao enviar e-mail via EmailJS: {msg_ej}")
          else:
            conn.close()
            st.error("Este e-mail não se encontra registado no sistema.")

      if btn_voltar_login:
        st.session_state["modo_recuperacao"] = False
        st.rerun()
