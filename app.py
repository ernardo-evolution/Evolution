from datetime import datetime, timedelta
import hashlib
import hmac
import os
import re
import sqlite3
import pandas as pd
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Evolution | Gestão Online",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. IDENTIDADE VISUAL OFICIAL ---
st.markdown("""
    <style>
    :root {
        --bg-deep: #080B11;
        --bg-graphite: #111722;
        --bg-surface: #151C27;
        --border-color: #293343;
        --text-main: #F5F7FA;
        --text-secondary: #A7B2C3;
        --accent-blue: #087BFF;
        --accent-glow: #00BFFF;
    }
    
    .stApp {
        background-color: var(--bg-deep);
        color: var(--text-main);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1, h2, h3, h4 {
        color: var(--text-main);
        letter-spacing: -0.025em;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-graphite);
        border-right: 1px solid var(--border-color);
    }
    
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background-color: var(--bg-graphite);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "evolution_gestao.db"

# --- 3. SEGURANÇA E HASH SEGURO (PBKDF2 NATIVO) ---
def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro usando PBKDF2 com salt aleatório."""
    salt = os.urandom(16)
    # 100.000 iterações para máxima segurança corporativa
    h = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + h.hex()

def verificar_e_migrar_senha(senha_fornecida: str, hash_armazenado: str) -> tuple[bool, str | None]:
    """
    Verifica senhas no formato seguro PBKDF2 ou em SHA-256 legado,
    migrando automaticamente contas antigas para o novo formato seguro.
    """
    if not hash_armazenado:
        return False, None
    
    # Formato moderno PBKDF2 (contém ':' separando o salt do hash)
    if ':' in hash_armazenado:
        try:
            salt_hex, hash_hex = hash_armazenado.split(':')
            salt = bytes.fromhex(salt_hex)
            h_f = hashlib.pbkdf2_hmac('sha256', senha_fornecida.encode('utf-8'), salt, 100000)
            valido = hmac.compare_digest(h_f.hex(), hash_hex)
            return valido, None
        except Exception:
            return False, None

    # Compatibilidade com SHA-256 simples legado
    sha256_antigo = hashlib.sha256(senha_fornecida.encode('utf-8')).hexdigest()
    if hmac.compare_digest(sha256_antigo, hash_armazenado):
        novo_hash = gerar_hash_senha(senha_fornecida)
        return True, novo_hash

    return False, None

def validar_forca_senha(senha: str) -> str | None:
    if len(senha) < 8:
        return "A palavra-passe deve ter pelo menos 8 caracteres."
    if not re.search(r"[a-z]", senha):
        return "A palavra-passe deve conter pelo menos uma letra minúscula."
    if not re.search(r"[0-9]", senha):
        return "A palavra-passe deve conter pelo menos um número."
    return None

def validar_email(email: str) -> bool:
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(padrao, email) is not None

# --- 4. BASE DE DADOS E MIGRAÇÕES ---
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            senha TEXT,
            nivel TEXT DEFAULT 'Funcionário',
            ativo INTEGER DEFAULT 1,
            email_verificado INTEGER DEFAULT 1,
            codigo_verificacao TEXT,
            token_recuperacao TEXT,
            token_expiracao TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            cidade TEXT,
            data_cadastro TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            produto TEXT,
            quantidade INTEGER,
            valor_total REAL,
            data_venda TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            email TEXT,
            acao TEXT,
            detalhes TEXT,
            resultado TEXT,
            data_hora TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo TEXT UNIQUE,
            usuario_email TEXT,
            nome TEXT,
            categoria TEXT,
            assunto TEXT,
            descricao TEXT,
            prioridade TEXT,
            estado TEXT DEFAULT 'Aberto',
            data_hora TEXT
        )
    """)
    
    conn.commit()

    def garantir_coluna(tabela, coluna, definicao):
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = [col[1] for col in cursor.fetchall()]
        if coluna not in colunas:
            cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
            conn.commit()

    garantir_coluna("usuarios", "email_verificado", "INTEGER DEFAULT 1")
    garantir_coluna("usuarios", "codigo_verificacao", "TEXT")
    garantir_coluna("usuarios", "token_recuperacao", "TEXT")
    garantir_coluna("usuarios", "token_expiracao", "TEXT")

    conn.close()
except Exception as e:
    st.error(f"Erro crítico na Base de Dados: {e}")

def registar_log(usuario, email, acao, detalhes, resultado):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            "INSERT INTO historico (usuario, email, acao, detalhes, resultado, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
            (usuario or "Sistema", email or "N/D", acao, detalhes, resultado, data_hora)
        )
        conn.commit()
        conn.close()
    except Exception as ex:
        print(f"Erro ao registar log: {ex}")

# --- 5. SESSÃO E ESTADO DA APLICAÇÃO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = ""
if "email_atual" not in st.session_state:
    st.session_state["email_atual"] = ""
if "nivel_acesso" not in st.session_state:
    st.session_state["nivel_acesso"] = ""
if "email_input" not in st.session_state:
    st.session_state["email_input"] = ""
if "modo_recuperacao" not in st.session_state:
    st.session_state["modo_recuperacao"] = False

# --- 6. BARRA LATERAL E NAVEGAÇÃO ---
menu = "Visão geral"
with st.sidebar:
    st.markdown("### ⚡ EVOLUTION")
    st.caption("GESTÃO ONLINE")
    st.markdown("---")
    
    if st.session_state["autenticado"]:
        st.markdown(f"👤 **{st.session_state['usuario_atual']}**")
        st.caption(f"📧 {st.session_state['email_atual']}")
        st.caption(f"🔑 Nível: {st.session_state['nivel_acesso']}")
        st.markdown("---")
        
        opcoes = [
            "Visão geral", "Vendas", "Clientes", "Produtos", 
            "Estoque", "Relatórios", "Ajuda e Suporte", "Configurações"
        ]
        if st.session_state["nivel_acesso"] == "Administrador":
            opcoes.append("Administração")
            
        menu = st.selectbox("Navegação", opcoes, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Terminar sessão", use_container_width=True):
            registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Logout", "Encerramento de sessão", "Sucesso")
            st.session_state["autenticado"] = False
            st.session_state["usuario_atual"] = ""
            st.session_state["email_atual"] = ""
            st.session_state["nivel_acesso"] = ""
            st.success("Sessão encerrada com sucesso.")
            st.rerun()
    else:
        st.info("Efetue login na página principal para aceder às ferramentas.")

# --- 7. FLUXO DE ENTRADA ---
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("## ⚡ EVOLUTION")
        st.caption("GESTÃO ONLINE")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state["modo_recuperacao"]:
            st.markdown("### Recuperação de Acesso")
            st.caption("Informe o seu e-mail corporativo cadastrado para iniciar a recuperação.")
            
            with st.form("form_recuperacao"):
                email_rec = st.text_input("E-mail corporativo", placeholder="nome@empresa.com").strip().lower()
                enviar_rec = st.form_submit_button("Enviar instruções", use_container_width=True)
                
                if enviar_rec:
                    if validar_email(email_rec):
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_rec,))
                        existe = cursor.fetchone()
                        
                        if existe:
                            import secrets
                            token_seguro = secrets.token_hex(16)
                            exp = datetime.now() + timedelta(hours=1)
                            cursor.execute("UPDATE usuarios SET token_recuperacao = ?, token_expiracao = ? WHERE email = ?", (token_seguro, str(exp), email_rec))
                            conn.commit()
                            registar_log("Sistema", email_rec, "Recuperação de Senha", "Token de recuperação gerado", "Sucesso")
                        conn.close()
                        
                        st.success("Se existir uma conta elegível para este endereço, enviaremos as instruções de recuperação.")
                    else:
                        st.error("Formato de e-mail inválido.")
            
            if st.button("Voltar ao Login", use_container_width=True):
                st.session_state["modo_recuperacao"] = False
                st.rerun()
                
        else:
            tab_login, tab_registo, tab_ajuda = st.tabs([
                "🔑 Já tenho uma conta (Entrar)", 
                "📝 Ainda não tenho uma conta (Criar)", 
                "❓ Central de Ajuda"
            ])
            
            with tab_login:
                st.markdown("### Bem-vindo de volta")
                st.caption("Aceda com o seu e-mail e palavra-passe cadastrados.")
                
                with st.form("form_login_principal"):
                    email_l = st.text_input("E-mail corporativo", placeholder="nome@empresa.com", value=st.session_state["email_input"]).strip().lower()
                    senha_l = st.text_input("Palavra-passe", type="password", placeholder="Digite a sua palavra-passe")
                    lembrar_me = st.checkbox("Lembrar de mim neste dispositivo")
                    btn_entrar = st.form_submit_button("Entrar na plataforma", use_container_width=True)
                    
                    if btn_entrar:
                        st.session_state["email_input"] = email_l
                        if not email_l or not senha_l:
                            st.warning("Preencha todos os campos obrigatórios.")
                        elif not validar_email(email_l):
                            st.error("Formato de e-mail inválido.")
                        else:
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT id, nome, nivel, senha, ativo, email_verificado, email FROM usuarios WHERE email = ?", 
                                (email_l,)
                            )
                            user_data = cursor.fetchone()
                            
                            if not user_data:
                                conn.close()
                                registar_log("Anónimo", email_l, "Login", "Tentativa de acesso com e-mail não cadastrado", "Falha")
                                st.error("Não foi possível entrar. Verifique os seus dados e tente novamente.")
                            else:
                                u_id, u_nome, u_nivel, u_senha_hash, u_ativo, u_verificado, u_email = user_data
                                
                                if u_ativo != 1:
                                    conn.close()
                                    registar_log(u_nome, u_email, "Login", "Tentativa em conta bloqueada/desativada", "Bloqueado")
                                    st.error("A sua conta encontra-se desativada ou bloqueada. Por favor, entre em contacto com a Central de Ajuda.")
                                elif u_verificado != 1:
                                    conn.close()
                                    registar_log(u_nome, u_email, "Login", "Tentativa em conta pendente de confirmação", "Pendente")
                                    st.warning("O seu e-mail ainda não foi confirmado.")
                                else:
                                    valido, novo_hash = verificar_e_migrar_senha(senha_l, u_senha_hash)
                                    
                                    if valido:
                                        if novo_hash:
                                            cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (novo_hash, u_id))
                                            conn.commit()
                                            registar_log(u_nome, u_email, "Migração de Segurança", "Senha atualizada para o formato seguro", "Sucesso")
                                        
                                        conn.close()
                                        st.session_state["autenticado"] = True
                                        st.session_state["usuario_atual"] = u_nome
                                        st.session_state["nivel_acesso"] = u_nivel
                                        st.session_state["email_atual"] = u_email
                                        
                                        registar_log(u_nome, u_email, "Login", "Autenticação bem-sucedida", "Sucesso")
                                        st.success("Sessão iniciada com sucesso!")
                                        st.rerun()
                                    else:
                                        conn.close()
                                        registar_log(u_nome, u_email, "Login", "Palavra-passe incorreta", "Falha")
                                        st.error("Não foi possível entrar. Verifique os seus dados e tente novamente.")
                
                if st.button("Esqueci a minha palavra-passe", type="tertiary"):
                    st.session_state["modo_recuperacao"] = True
                    st.rerun()

            with tab_registo:
                st.markdown("### Crie a sua conta")
                st.caption("Cadastre-se para obter acesso à plataforma Evolution Gestão Online.")
                
                with st.form("form_registo_principal"):
                    r_nome = st.text_input("Nome completo")
                    r_user = st.text_input("Nome de utilizador (Username)")
                    r_email = st.text_input("E-mail corporativo", placeholder="nome@empresa.com").strip().lower()
                    r_senha = st.text_input("Palavra-passe", type="password", placeholder="Mín. 8 caracteres, com letra e número")
                    r_conf = st.text_input("Confirmar palavra-passe", type="password")
                    btn_cadastrar = st.form_submit_button("Criar conta", use_container_width=True)
                    
                    if btn_cadastrar:
                        erro_pwd = validar_forca_senha(r_senha)
                        if not r_nome or not r_user or not r_email or not r_senha:
                            st.warning("Preencha todos os campos obrigatórios.")
                        elif not validar_email(r_email):
                            st.error("E-mail com formato inválido.")
                        elif r_senha != r_conf:
                            st.error("As palavras-passe não coincidem.")
                        elif erro_pwd:
                            st.error(erro_pwd)
                        else:
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM usuarios WHERE email = ? OR username = ?", (r_email, r_user))
                            duplicado = cursor.fetchone()
                            
                            if duplicado:
                                conn.close()
                                st.error("O e-mail ou nome de utilizador já se encontra registado.")
                            else:
                                cursor.execute("SELECT COUNT(*) FROM usuarios")
                                total_u = cursor.fetchone()[0]
                                nivel_atribuido = "Administrador" if total_u == 0 else "Funcionário"
                                
                                hash_seguro = gerar_hash_senha(r_senha)
                                cursor.execute(
                                    "INSERT INTO usuarios (nome, username, email, senha, nivel, ativo, email_verificado) VALUES (?, ?, ?, ?, ?, 1, 1)",
                                    (r_nome, r_user, r_email, hash_seguro, nivel_atribuido)
                                )
                                conn.commit()
                                conn.close()
                                registar_log(r_nome, r_email, "Registo", f"Conta criada com nível {nivel_atribuido}", "Sucesso")
                                st.success("Conta criada com sucesso! Mude para a aba 'Já tenho uma conta' para iniciar sessão.")

            with tab_ajuda:
                st.markdown("### Central de Ajuda")
                st.caption("Como podemos ajudar?")
                
                pesquisa_ajuda = st.text_input("Pesquise uma dúvida...", placeholder="Ex: login, senha, relatórios")
                
                st.markdown("**Perguntas Frequentes:**")
                st.markdown("- **Já tenho conta, como entro?** Selecione a aba 'Já tenho uma conta', digite o seu e-mail e palavra-passe.")
                st.markdown("- **Esqueci a minha senha:** Clique no link 'Esqueci a minha palavra-passe' no formulário de login.")
                st.markdown("- **Conta desativada:** Entre em contacto através do formulário abaixo para solicitar suporte.")
                
                st.markdown("---")
                st.markdown("#### Abrir Chamado de Suporte")
                with st.form("form_suporte_publico"):
                    s_nome = st.text_input("O seu nome")
                    s_email = st.text_input("O seu e-mail")
                    s_cat = st.selectbox("Categoria", ["Acesso à conta", "Conta bloqueada", "Problemas técnicos", "Outras dúvidas"])
                    s_desc = st.text_area("Descrição detalhada do problema")
                    btn_chamado = st.form_submit_button("Enviar solicitação")
                    
                    if btn_chamado:
                        if s_nome and s_email and s_desc:
                            import secrets
                            proto = "EVO-" + secrets.token_hex(4).upper()
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO chamados (protocolo, usuario_email, nome, categoria, assunto, descricao, prioridade, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (proto, s_email, s_nome, s_cat, "Atendimento Público", s_desc, "Normal", datetime.now().strftime("%d/%m/%Y %H:%M"))
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Solicitação registada com sucesso! Guarde o protocolo: **{proto}**")
                        else:
                            st.warning("Preencha todos os campos obrigatórios para abrir o chamado.")

# --- 8. PAINEL PRINCIPAL E MÓDULOS OPERACIONAIS ---
else:
    conn = sqlite3.connect(DB_FILE)
    
    if menu == "Visão geral":
        st.header("Visão geral")
        st.markdown(f"Bem-vindo(a) de volta, **{st.session_state['usuario_atual']}**.")
        st.markdown("---")
        
        try:
            df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
            df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
            df_produtos = pd.read_sql_query("SELECT * FROM produtos", conn)
            
            fat_total = df_vendas["valor_total"].sum() if not df_vendas.empty else 0.0
            num_vendas = len(df_vendas)
            num_clientes = len(df_clientes)
            num_produtos = len(df_produtos)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento Total", f"R$ {fat_total:,.2f}")
            c2.metric("Total de Vendas", num_vendas)
            c3.metric("Clientes Registados", num_clientes)
            c4.metric("Produtos Cadastrados", num_produtos)
            
            st.markdown("---")
            if not df_vendas.empty:
                st.subheader("Evolução de Vendas")
                st.bar_chart(df_vendas, x="data_venda", y="valor_total")
            else:
                st.info("Sem dados de vendas registados para exibição de gráficos.")
        except Exception as e:
            st.error(f"Erro ao carregar métricas do painel: {e}")

    elif menu == "Vendas":
        st.header("Gestão de Vendas")
        df_cli = pd.read_sql_query("SELECT nome FROM clientes", conn)
        df_prod = pd.read_sql_query("SELECT nome, preco FROM produtos", conn)
        
        if df_cli.empty or df_prod.empty:
            st.warning("Cadastre pelo menos um cliente e um produto antes de efetuar vendas.")
        else:
            with st.form("form_registo_venda"):
                v_cli = st.selectbox("Cliente", df_cli["nome"].tolist())
                v_prod = st.selectbox("Produto", df_prod["nome"].tolist())
                v_qtd = st.number_input("Quantidade", min_value=1, step=1)
                btn_venda = st.form_submit_button("Concluir Venda")
                
                if btn_venda:
                    preco_unit = df_prod.loc[df_prod["nome"] == v_prod, "preco"].values[0]
                    total_v = preco_unit * v_qtd
                    data_v = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO vendas (cliente, produto, quantidade, valor_total, data_venda) VALUES (?, ?, ?, ?, ?)",
                        (v_cli, v_prod, v_qtd, total_v, data_v)
                    )
                    conn.commit()
                    registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Venda", f"Venda de {v_qtd}x {v_prod} para {v_cli}", "Sucesso")
                    st.success(f"Venda registada com sucesso! Total: R$ {total_v:,.2f}")
                    st.rerun()
                    
        st.markdown("---")
        st.subheader("Histórico de Vendas")
        df_hist_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
        st.dataframe(df_hist_vendas, use_container_width=True)

    elif menu == "Clientes":
        st.header("Gestão de Clientes")
        with st.form("form_cliente_novo"):
            c_nome = st.text_input("Nome do Cliente")
            c_email = st.text_input("E-mail")
            c_tel = st.text_input("Telefone")
            c_cid = st.text_input("Cidade")
            btn_c = st.form_submit_button("Guardar Cliente")
            
            if btn_c and c_nome:
                cursor = conn.cursor()
                data_cad = datetime.now().strftime("%d/%m/%Y")
                cursor.execute(
                    "INSERT INTO clientes (nome, email, telefone, cidade, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                    (c_nome, c_email, c_tel, c_cid, data_cad)
                )
                conn.commit()
                registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Cliente", f"Cliente {c_nome} criado", "Sucesso")
                st.success(f"Cliente '{c_nome}' guardado com sucesso!")
                st.rerun()
                
        st.markdown("---")
        df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df_clientes, use_container_width=True)

    elif menu == "Produtos":
        st.header("Gestão de Produtos")
        with st.form("form_produto_novo"):
            p_nome = st.text_input("Nome do Produto")
            p_preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
            p_stock = st.number_input("Stock Inicial", min_value=0, step=1)
            btn_p = st.form_submit_button("Guardar Produto")
            
            if btn_p and p_nome:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO produtos (nome, preco, stock) VALUES (?, ?, ?)",
                    (p_nome, p_preco, p_stock)
                )
                conn.commit()
                registar_log(st.session_state["usuario_atual"], st.session_state["email_atual"], "Produto", f"Produto {p_nome} criado", "Sucesso")
                st.success(f"Produto '{p_nome}' guardado com sucesso!")
                st.rerun()
                
        st.markdown("---")
        df_produtos = pd.read_sql_query("SELECT * FROM produtos", conn)
        st.dataframe(df_produtos, use_container_width=True)

    elif menu == "Estoque":
        st.header("Controle de Estoque")
        df_estoque = pd.read_sql_query("SELECT id, nome, stock, preco FROM produtos", conn)
        st.dataframe(df_estoque, use_container_width=True)

    elif menu == "Relatórios":
        st.header("Relatórios e Indicadores")
        try:
            df_v = pd.read_sql_query("SELECT * FROM vendas", conn)
            if not df_v.empty:
                st.dataframe(df_v, use_container_width=True)
            else:
                st.info("Sem dados para exibição de relatórios.")
        except Exception as e:
            st.error(f"Erro ao gerar relatórios: {e}")

    elif menu == "Ajuda e Suporte":
        st.header("Central de Ajuda e Suporte")
        st.markdown("---")
        st.subheader("Abrir Novo Chamado")
        with st.form("form_chamado_interno"):
            cat_c = st.selectbox("Categoria", ["Acesso à conta", "Gestão de usuários", "Problemas técnicos", "Outras dúvidas"])
            assunto_c = st.text_input("Assunto")
            desc_c = st.text_area("Descrição detalhada")
            prioridade_c = st.selectbox("Prioridade", ["Baixa", "Normal", "Alta"])
            btn_env_chamado = st.form_submit_button("Enviar solicitação")
            
            if btn_env_chamado and assunto_c and desc_c:
                import secrets
                proto = "EVO-" + secrets.token_hex(4).upper()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chamados (protocolo, usuario_email, nome, categoria, assunto, descricao, prioridade, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (proto, st.session_state["email_atual"], st.session_state["usuario_atual"], cat_c, assunto_c, desc_c, prioridade_c, datetime.now().strftime("%d/%m/%Y %H:%M"))
                )
                conn.commit()
                st.success(f"Chamado aberto com sucesso! Protocolo: **{proto}**")
            elif btn_env_chamado:
                st.warning("Preencha o assunto e a descrição.")
                
        st.markdown("---")
        st.subheader("Meus Chamados")
        df_meus_chamados = pd.read_sql_query("SELECT protocolo, categoria, assunto, prioridade, estado, data_hora FROM chamados WHERE usuario_email = ?", conn, params=(st.session_state["email_atual"],))
        st.dataframe(df_meus_chamados, use_container_width=True)

    elif menu == "Configurações":
        st.header("Configurações da Conta")
        st.markdown(f"**Nome:** {st.session_state['usuario_atual']}")
        st.markdown(f"**E-mail:** {st.session_state['email_atual']}")
        st.markdown(f"**Nível de Acesso:** {st.session_state['nivel_acesso']}")

    elif menu == "Administração" and st.session_state["nivel_acesso"] == "Administrador":
        st.header("Painel Administrativo e Auditoria")
        tab_users, tab_logs, tab_admin_chamados = st.tabs(["Gerir Utilizadores", "Logs do Sistema", "Gestão de Chamados"])
        
        with tab_users:
            st.subheader("Utilizadores Registados")
            df_users = pd.read_sql_query("SELECT id, nome, username, email, nivel, ativo, email_verificado FROM usuarios", conn)
            st.dataframe(df_users, use_container_width=True)
            
        with tab_logs:
            st.subheader("Registo de Auditoria")
            df_logs = pd.read_sql_query("SELECT * FROM historico ORDER BY id DESC LIMIT 100", conn)
            st.dataframe(df_logs, use_container_width=True)
            
        with tab_admin_chamados:
            st.subheader("Todos os Chamados de Suporte")
            df_all_c = pd.read_sql_query("SELECT * FROM chamados", conn)
            st.dataframe(df_all_c, use_container_width=True)

    conn.close()
