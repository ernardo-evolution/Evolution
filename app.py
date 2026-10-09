# ==========================================
  # 9. TAREFAS
  # ==========================================
  elif menu == t["tarefas"]:
    st.header("📝 Gestor Integrado de Tarefas")
    with st.form("form_tar"):
      tit = st.text_input("Título da Tarefa")
      resp = st.text_input(
          "Responsável", value=st.session_state["usuario_atual"]
      )
      prazo = st.text_input("Prazo (ex: 2 dias)")
      prio = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
      rel = st.text_input("Relacionamento (Cliente/Pedido)")
      if st.form_submit_button("Criar Tarefa"):
        if tit:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          data_h = datetime.now().strftime("%d/%m/%Y")
          cursor.execute(
              "INSERT INTO tarefas (titulo, responsavel, prazo, prioridade,"
              " status, relacionamento, data_criacao) VALUES (?, ?, ?, ?, ?, ?,"
              " ?)",
              (tit, resp, prazo, prio, "Pendente", rel, data_h),
          )
          conn.commit()
          conn.close()
          st.success("Tarefa criada com sucesso!")
          st.rerun()

    st.subheader("Lista de Tarefas Ativas")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, responsavel, prazo, prioridade, status FROM tarefas"
    )
    tarefas = cursor.fetchall()
    conn.close()

    for tr in tarefas:
      st.write(
          f"📌 **{tr[1]}** (Resp: {tr[2]} | Prazo: {tr[3]} | Prioridade:"
          f" {tr[4]} | Status: **{tr[5]}**)"
      )
      if tr[5] != "Concluída" and st.button(
          f"Concluir Tarefa #{tr[0]}", key=f"t_{tr[0]}"
      ):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tarefas SET status = 'Concluída' WHERE id = ?", (tr[0],)
        )
        conn.commit()
        conn.close()
        st.success("Tarefa concluída!")
        st.rerun()
