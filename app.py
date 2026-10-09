def init_db():
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                pais TEXT,
                pais_registro TEXT,
                moeda TEXT,
                simbolo TEXT,
                idioma TEXT,
                fuso TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                senha TEXT,
                nivel TEXT,
                session_token TEXT,
                token_expiry TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                telefone TEXT,
                pais TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                preco REAL,
                quantidade_estoque INTEGER,
                estoque_minimo INTEGER,
                moeda TEXT,
                simbolo TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                produto TEXT,
                quantidade INTEGER,
                valor_unitario REAL,
                valor_total REAL,
                moeda_original TEXT,
                data_hora TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                produto TEXT,
                quantidade INTEGER,
                status_venda TEXT,
                status_separacao TEXT,
                status_envio TEXT,
                status_pedido TEXT,
                data_criacao TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT,
                responsavel TEXT,
                prazo TEXT,
                prioridade TEXT,
                status TEXT,
                relacionamento TEXT,
                data_criacao TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                acao TEXT,
                detalhes TEXT,
                data_hora TEXT
            )
        """)

    # Verificação dinâmica e segura de colunas na tabela produtos
    cursor.execute("PRAGMA table_info(produtos)")
    colunas_produtos = [col[1] for col in cursor.fetchall()]
    if "estoque_minimo" not in colunas_produtos:
      cursor.execute(
          "ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 5"
      )

    # Verificação para utilizadores (caso venham de versões anteriores)
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas_usuarios = [col[1] for col in cursor.fetchall()]
    for col_falk in ["senha", "session_token", "token_expiry"]:
      if col_falk not in colunas_usuarios:
        cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {col_falk} TEXT")

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM empresa")
    if cursor.fetchone()[0] == 0:
      cursor.execute(
          "INSERT INTO empresa (nome, pais, pais_registro, moeda, simbolo,"
          " idioma, fuso) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (
              "Evolution Corp Brasil",
              "Brasil",
              "Brasil",
              "BRL",
              "R$",
              "Português",
              "UTC-3",
          ),
      )
      conn.commit()

    conn.close()
  except Exception as db_err:
    st.error(f"Erro ao inicializar base de dados: {db_err}")
