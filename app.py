# --- MÓDULO: VENDAS ---
  elif menu == t["vendas"]:
    st.header("🛒 Registar Venda")
    try:
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute("SELECT nome FROM clientes")
      cli_list = [c[0] for c in cursor.fetchall()]
      cursor.execute(
          "SELECT nome, preco, quantidade_estoque FROM produtos WHERE"
          " quantidade_estoque > 0"
      )
      prod_data = cursor.fetchall()
      conn.close()

      if not cli_list or not prod_data:
        st.warning(
            "Necessita de ter clientes e produtos com estoque para efetuar"
            " vendas."
        )
      else:
        prod_dict = {p[0]: {"preco": p[1], "estoque": p[2]} for p in prod_data}
        with st.form("form_registar_venda"):
          cli_sel = st.selectbox("Cliente", cli_list)
          prod_sel = st.selectbox("Produto", list(prod_dict.keys()))
          qtd_venda = st.number_input("Quantidade", min_value=1, value=1)
          btn_vender = st.form_submit_button("Concluir Venda")

          if btn_vender:
            preco_unit = prod_dict[prod_sel]["preco"]
            estoque_atual = prod_dict[prod_sel]["estoque"]
            if qtd_venda > estoque_atual:
              st.error("Quantidade superior ao estoque disponível!")
            else:
              val_total = qtd_venda * preco_unit
              data_h = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

              conn = sqlite3.connect(DB_FILE)
              cursor = conn.cursor()
              cursor.execute(
                  "INSERT INTO vendas (cliente, produto, quantidade,"
                  " valor_unitario, valor_total, moeda_original, data_hora)"
                  " VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (
                      cli_sel,
                      prod_sel,
                      qtd_venda,
                      preco_unit,
                      val_total,
                      emp["moeda"],
                      data_h,
                  ),
              )
              cursor.execute(
                  "UPDATE produtos SET quantidade_estoque = quantidade_estoque -"
                  " ? WHERE nome = ?",
                  (qtd_venda, prod_sel),
              )
              conn.commit()
              conn.close()

              registrar_historico(
                  st.session_state["usuario_atual"],
                  "Nova Venda",
                  f"Venda de {qtd_venda}x {prod_sel} para {cli_sel}.",
              )
              st.success("Venda efetuada com sucesso e estoque atualizado!")
              st.rerun()
    except Exception as e:
      st.error(f"Erro no módulo de vendas: {e}")
