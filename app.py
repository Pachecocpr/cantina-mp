import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Cantina dos Ministérios", page_icon="✝️", layout="wide")

# Arquivos de dados
ARQUIVO_GRUPOS = "grupos.csv"
ARQUIVO_ESTOQUE = "estoque_cantina.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"
ARQUIVO_USUARIOS = "usuarios.csv"

URL_BASE = "https://cantina-mp-qpwibpbbdhxh85b23yopiy.streamlit.app"

# LISTA DE MINISTÉRIOS COM ILUSTRAÇÕES DE TEMÁTICA BÍBLICA E CRISTÃ
GRUPOS_PADRAO = [
    {
        "Grupo_ID": "Min. da Família", 
        "Imagem_URL": "https://images.unsplash.com/photo-1544027993-37dbfe43562a?auto=format&fit=crop&w=800&q=80" # Família unida em comunhão
    },
    {
        "Grupo_ID": "Min. de Jovens", 
        "Imagem_URL": "https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=800&q=80" # Bíblia Sagrada e Cruz de Cristo
    },
    {
        "Grupo_ID": "Min. Cura e Libertação", 
        "Imagem_URL": "https://images.unsplash.com/photo-1507692049790-de58290a4334?auto=format&fit=crop&w=800&q=80" # Mãos postas em fé e oração
    },
    {
        "Grupo_ID": "Min. de Empresários", 
        "Imagem_URL": "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=800&q=80" # Estudo da Palavra para sabedoria
    },
    {
        "Grupo_ID": "Min. de Homens", 
        "Imagem_URL": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?auto=format&fit=crop&w=800&q=80" # Homens reunidos em comunhão cristã
    },
    {
        "Grupo_ID": "Min. das Mulheres", 
        "Imagem_URL": "https://images.unsplash.com/photo-1515162305285-0293e4767cc2?auto=format&fit=crop&w=800&q=80" # Mulheres em momento de oração
    },
    {
        "Grupo_ID": "Min. da Melhor idade", 
        "Imagem_URL": "https://images.unsplash.com/photo-1516307365426-bea591f05011?auto=format&fit=crop&w=800&q=80" # Idosos lendo a Bíblia
    },
    {
        "Grupo_ID": "Min. de Juniores", 
        "Imagem_URL": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?auto=format&fit=crop&w=800&q=80" # Pré-adolescentes na Escola Dominical
    },
    {
        "Grupo_ID": "Min. das Crianças", 
        "Imagem_URL": "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?auto=format&fit=crop&w=800&q=80" # Crianças aprendendo lições bíblicas
    },
    {
        "Grupo_ID": "Instruir Para Crescer", 
        "Imagem_URL": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80" # Livro da Bíblia Sagrada aberto
    },
    {
        "Grupo_ID": "Min. de Dança", 
        "Imagem_URL": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=800&q=80" # Dança e adoração
    },
    {
        "Grupo_ID": "Min. de Louvor", 
        "Imagem_URL": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80" # Instrumentos no altar em adoração
    },
]

# --- INICIALIZAÇÃO DE DADOS E CRIAÇÃO DO ADMIN ---

def inicializar_arquivos():
    # Atualiza sempre os grupos para garantir os links válidos de imagens bíblicas
    pd.DataFrame(GRUPOS_PADRAO).to_csv(ARQUIVO_GRUPOS, index=False)

    # Força a criação/recriação da conta Admin garantindo o acesso (admin / 123)
    df_usr_padrao = pd.DataFrame([
        {"Usuario": "admin", "Senha": "123", "Role": "SuperAdmin", "Grupo_ID": "TODOS"}
    ])
    
    if not os.path.exists(ARQUIVO_USUARIOS) or os.path.getsize(ARQUIVO_USUARIOS) == 0:
        df_usr_padrao.to_csv(ARQUIVO_USUARIOS, index=False)
    else:
        # Garante que a linha do admin exista mesmo que o arquivo já tenha outros dados
        df_existente = pd.read_csv(ARQUIVO_USUARIOS)
        if df_existente[df_existente["Usuario"] == "admin"].empty:
            df_unificado = pd.concat([df_existente, df_usr_padrao], ignore_index=True)
            df_unificado.to_csv(ARQUIVO_USUARIOS, index=False)

    if not os.path.exists(ARQUIVO_ESTOQUE) or os.path.getsize(ARQUIVO_ESTOQUE) == 0:
        pd.DataFrame(columns=["Grupo_ID", "Produto", "Estoque", "Minimo_Recomendado", "Preco"]).to_csv(ARQUIVO_ESTOQUE, index=False)

    if not os.path.exists(ARQUIVO_VENDAS) or os.path.getsize(ARQUIVO_VENDAS) == 0:
        pd.DataFrame(columns=["Grupo_ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento"]).to_csv(ARQUIVO_VENDAS, index=False)

    if not os.path.exists(ARQUIVO_PEDIDOS) or os.path.getsize(ARQUIVO_PEDIDOS) == 0:
        pd.DataFrame(columns=["ID", "Grupo_ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"]).to_csv(ARQUIVO_PEDIDOS, index=False)

inicializar_arquivos()

# --- FUNÇÕES AUXILIARES ---

def carregar_df(caminho):
    return pd.read_csv(caminho) if os.path.exists(caminho) else pd.DataFrame()

def salvar_df(df, caminho):
    df.to_csv(caminho, index=False)

def gerar_qrcode(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- SESSÃO E AUTENTICAÇÃO ---

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state.role = "Cliente"
    st.session_state.grupo_id = None

st.sidebar.title("🔐 Login de Gestão")

df_usuarios = carregar_df(ARQUIVO_USUARIOS)

if st.session_state.usuario_logado is None:
    with st.sidebar.expander("Acesso para Gestores e Admin", expanded=True):
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary"):
            u_clean = str(user_input).strip()
            p_clean = str(pass_input).strip()
            usr_match = df_usuarios[(df_usuarios["Usuario"].astype(str) == u_clean) & (df_usuarios["Senha"].astype(str) == p_clean)]
            
            if not usr_match.empty:
                info_usr = usr_match.iloc[0]
                st.session_state.usuario_logado = info_usr["Usuario"]
                st.session_state.role = info_usr["Role"]
                st.session_state.grupo_id = info_usr["Grupo_ID"]
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha inválidos.")
else:
    st.sidebar.info(f"👤 **{st.session_state.usuario_logado}** ({st.session_state.role})")
    if st.button("Sair (Logout)"):
        st.session_state.usuario_logado = None
        st.session_state.role = "Cliente"
        st.session_state.grupo_id = None
        st.rerun()

st.title("✝️ Cantina dos Ministérios")

# --- TRATAMENTO DOS DADOS ---

df_grupos = carregar_df(ARQUIVO_GRUPOS)
df_estoque = carregar_df(ARQUIVO_ESTOQUE)
df_pedidos = carregar_df(ARQUIVO_PEDIDOS)

lista_de_grupos = df_grupos["Grupo_ID"].tolist() if not df_grupos.empty else []

if st.session_state.role == "SuperAdmin":
    st.sidebar.subheader("👑 Painel Admin")
    grupo_ativo = st.sidebar.selectbox("Visualizar Dados do Grupo:", ["TODOS"] + lista_de_grupos)
elif st.session_state.role == "Gestor":
    grupo_ativo = st.session_state.grupo_id
    st.sidebar.info(f"Sua Cantina: **{grupo_ativo}**")
else:
    query_params = st.query_params
    grupo_param = query_params.get("grupo", None)
    
    if grupo_param and grupo_param in lista_de_grupos:
        grupo_ativo = grupo_param
    else:
        grupo_ativo = st.sidebar.selectbox("Escolha o Ministério / Grupo:", lista_de_grupos)

# --- NAVEGAÇÃO COMPATÍVEL ---
opcoes_menu = ["📱 Cardápio (Cliente)"]
if st.session_state.role in ["Gestor", "SuperAdmin"]:
    opcoes_menu.extend(["🔔 Pedidos Recebidos", "🛒 Venda Balcão", "⚙️ Gestão de Estoque", "📊 Histórico de Vendas", "📲 Gerar QR Code"])
if st.session_state.role == "SuperAdmin":
    opcoes_menu.append("👑 Administração Geral")

modo = st.sidebar.radio("Navegação do App:", opcoes_menu, horizontal=True)
st.divider()

# --- VISÃO 1: CARDÁPIO DO CLIENTE ---
if modo == "📱 Cardápio (Cliente)":
    if grupo_ativo != "TODOS":
        info_grupo = df_grupos[df_grupos["Grupo_ID"] == grupo_ativo]
        url_imagem = info_grupo["Imagem_URL"].values[0] if not info_grupo.empty else "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80"
        
        col_img, col_tit = st.columns([1, 3])
        with col_img:
            st.image(url_imagem, use_container_width=True)
        with col_tit:
            st.title(f"✨ {grupo_ativo}")
            st.subheader("Cardápio Digital da Cantina")
            st.caption("Faça seu pedido abaixo para ser preparado pela equipe.")
    else:
        st.header("📱 Cardápio Digital - Visão Geral")

    df_estoque_grp = df_estoque[df_estoque["Grupo_ID"] == grupo_ativo] if not df_estoque.empty else pd.DataFrame()
    df_pedidos_grp = df_pedidos[(df_pedidos["Grupo_ID"] == grupo_ativo) & (df_pedidos["Status"] == "Pendente")] if not df_pedidos.empty else pd.DataFrame()

    if df_estoque_grp.empty:
        st.warning(f"Nenhum produto cadastrado para a cantina **{grupo_ativo}** no momento.")
    else:
        reservas = df_pedidos_grp.groupby("Produto")["Quantidade"].sum().to_dict() if not df_pedidos_grp.empty else {}
        
        df_cardapio = df_estoque_grp.copy()
        df_cardapio["Estoque_Reservado"] = df_cardapio["Produto"].map(reservas).fillna(0).astype(int)
        df_cardapio["Estoque_Disponivel"] = df_cardapio["Estoque"] - df_cardapio["Estoque_Reservado"]
        
        df_disp = df_cardapio[df_cardapio["Estoque_Disponivel"] > 0]

        if df_disp.empty:
            st.error("⚠️ Todos os produtos desta cantina estão esgotados agora!")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form("form_cliente", clear_on_submit=True):
                    nome_cliente = st.text_input("Seu Nome *")
                    celular = st.text_input("Celular / WhatsApp *")
                    prod_sel = st.selectbox("Produto", df_disp["Produto"].tolist())
                    
                    linha_prod = df_disp[df_disp["Produto"] == prod_sel].iloc[0]
                    qtd_max = int(linha_prod["Estoque_Disponivel"])
                    preco_unit = float(linha_prod["Preco"])

                    qtd = st.number_input(f"Quantidade (Max: {qtd_max})", min_value=1, max_value=max(1, qtd_max), value=1)
                    pagto = st.radio("Pagamento", ["Pix", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Posterior"])

                    total = qtd * preco_unit
                    st.info(f"**Total:** R$ {total:.2f}")

                    if st.form_submit_button("🚀 Enviar Pedido", type="primary", use_container_width=True):
                        if not nome_cliente.strip() or not celular.strip():
                            st.warning("Preencha seu nome e celular.")
                        else:
                            novo_pedido = {
                                "ID": int(datetime.now().timestamp()),
                                "Grupo_ID": grupo_ativo,
                                "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Cliente": f"{nome_cliente.strip()} ({celular.strip()})",
                                "Produto": prod_sel,
                                "Quantidade": qtd,
                                "Valor_Total": round(total, 2),
                                "Forma_Pagamento": pagto,
                                "Status": "Pendente"
                            }
                            salvar_df(pd.concat([df_pedidos, pd.DataFrame([novo_pedido])], ignore_index=True), ARQUIVO_PEDIDOS)
                            st.balloons()
                            st.success("✅ Pedido enviado! Aguarde no balcão.")

            with col2:
                st.subheader("Itens Disponíveis")
                st.dataframe(df_disp[["Produto", "Preco", "Estoque_Disponivel"]].rename(columns={"Preco": "Preço (R$)", "Estoque_Disponivel": "Disponível"}), use_container_width=True, hide_index=True)

# --- VISÃO 2: PEDIDOS RECEBIDOS ---
elif modo == "🔔 Pedidos Recebidos":
    st.header(f"🔔 Pedidos Recebidos - {grupo_ativo}")
    df_vendas = carregar_df(ARQUIVO_VENDAS)

    filtro_pedidos = df_pedidos if grupo_ativo == "TODOS" else df_pedidos[df_pedidos["Grupo_ID"] == grupo_ativo]
    pendentes = filtro_pedidos[filtro_pedidos["Status"] == "Pendente"] if not filtro_pedidos.empty else pd.DataFrame()

    if pendentes.empty:
        st.info("Nenhum pedido pendente.")
    else:
        for idx, ped in pendentes.iterrows():
            with st.expander(f"📦 [{ped['Grupo_ID']}] {ped['Cliente']} - R$ {ped['Valor_Total']:.2f}", expanded=True):
                st.write(f"**Item:** {ped['Quantidade']}x {ped['Produto']} | **Pagamento:** {ped['Forma_Pagamento']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar", key=f"conf_{ped['ID']}", type="primary"):
                        mask = (df_estoque["Grupo_ID"] == ped["Grupo_ID"]) & (df_estoque["Produto"] == ped["Produto"])
                        if not df_estoque[mask].empty and df_estoque.loc[mask, "Estoque"].values[0] >= ped["Quantidade"]:
                            df_estoque.loc[mask, "Estoque"] -= ped["Quantidade"]
                            salvar_df(df_estoque, ARQUIVO_ESTOQUE)

                            nova_venda = ped.to_dict()
                            del nova_venda["ID"]
                            del nova_venda["Status"]
                            salvar_df(pd.concat([df_vendas, pd.DataFrame([nova_venda])], ignore_index=True), ARQUIVO_VENDAS)

                            df_pedidos.loc[df_pedidos["ID"] == ped["ID"], "Status"] = "Aprovado"
                            salvar_df(df_pedidos, ARQUIVO_PEDIDOS)
                            st.success("Aprovado!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente!")
                with col2:
                    if st.button("❌ Rejeitar", key=f"rej_{ped['ID']}"):
                        df_pedidos.loc[df_pedidos["ID"] == ped["ID"], "Status"] = "Rejeitado"
                        salvar_df(df_pedidos, ARQUIVO_PEDIDOS)
                        st.warning("Rejeitado.")
                        st.rerun()

# --- VISÃO 3: VENDAS BALCÃO ---
elif modo == "🛒 Venda Balcão":
    st.header(f"🛒 Venda Balcão - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        df_vendas = carregar_df(ARQUIVO_VENDAS)
        df_est_grp = df_estoque[df_estoque["Grupo_ID"] == grupo_ativo] if not df_estoque.empty else pd.DataFrame()

        if df_est_grp.empty:
            st.warning("Nenhum produto cadastrado.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                prod_sel = st.selectbox("Produto", df_est_grp["Produto"].tolist())
                linha_prod = df_est_grp[df_est_grp["Produto"] == prod_sel].iloc[0]
                qtd_est = int(linha_prod["Estoque"])
                preco = float(linha_prod["Preco"])

                qtd = st.number_input("Quantidade", min_value=1, max_value=max(1, qtd_est), value=1)
                pagto = st.radio("Pagamento", ["Pix", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Posterior"])
                total = qtd * preco
                st.info(f"**Total:** R$ {total:.2f}")

                if st.button("Confirmar Venda", type="primary"):
                    if qtd_est >= qtd:
                        mask = (df_estoque["Grupo_ID"] == grupo_ativo) & (df_estoque["Produto"] == prod_sel)
                        df_estoque.loc[mask, "Estoque"] -= qtd
                        salvar_df(df_estoque, ARQUIVO_ESTOQUE)
                        venda_dict = {
                            "Grupo_ID": grupo_ativo, "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Cliente": "Venda Balcão", "Produto": prod_sel, "Quantidade": qtd,
                            "Valor_Total": round(total, 2), "Forma_Pagamento": pagto
                        }
                        salvar_df(pd.concat([df_vendas, pd.DataFrame([venda_dict])], ignore_index=True), ARQUIVO_VENDAS)
                        st.success("Venda registrada!")
                        st.rerun()

            with col2:
                st.subheader("Estoque Local")
                st.dataframe(df_est_grp[["Produto", "Estoque", "Preco"]], use_container_width=True)

# --- VISÃO 4: GESTÃO DE ESTOQUE ---
elif modo == "⚙️ Gestão de Estoque":
    st.header(f"⚙️ Gestão de Estoque - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        with st.form("form_prod"):
            nome = st.text_input("Nome do Produto")
            qtd = st.number_input("Estoque", min_value=0, value=10)
            minimo = st.number_input("Estoque Mínimo", min_value=0, value=5)
            preco = st.number_input("Preço (R$)", min_value=0.0, value=5.00)

            if st.form_submit_button("Salvar / Atualizar Produto"):
                if nome.strip():
                    nome_limpo = nome.strip().capitalize()
                    mask = (df_estoque["Grupo_ID"] == grupo_ativo) & (df_estoque["Produto"] == nome_limpo)
                    if not df_estoque[mask].empty:
                        df_estoque.loc[mask, ["Estoque", "Minimo_Recomendado", "Preco"]] = [qtd, minimo, preco]
                    else:
                        nova_linha = {"Grupo_ID": grupo_ativo, "Produto": nome_limpo, "Estoque": qtd, "Minimo_Recomendado": minimo, "Preco": preco}
                        df_estoque = pd.concat([df_estoque, pd.DataFrame([nova_linha])], ignore_index=True)
                    salvar_df(df_estoque, ARQUIVO_ESTOQUE)
                    st.success("Produto salvo!")
                    st.rerun()

        st.dataframe(df_estoque[df_estoque["Grupo_ID"] == grupo_ativo], use_container_width=True)

# --- VISÃO 5: HISTÓRICO ---
elif modo == "📊 Histórico de Vendas":
    st.header(f"📊 Histórico de Vendas - {grupo_ativo}")
    df_vendas = carregar_df(ARQUIVO_VENDAS)
    filtro_vendas = df_vendas if grupo_ativo == "TODOS" else df_vendas[df_vendas["Grupo_ID"] == grupo_ativo]

    if not filtro_vendas.empty:
        st.metric("Faturamento Total", f"R$ {filtro_vendas['Valor_Total'].sum():.2f}")
        st.dataframe(filtro_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda cadastrada.")

# --- VISÃO 6: QR CODE ---
elif modo == "📲 Gerar QR Code":
    st.header(f"📲 QR Code - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        url_grupo = f"{URL_BASE}?grupo={grupo_ativo}"
        qr_bytes = gerar_qrcode(url_grupo)
        st.image(qr_bytes, width=250)
        st.code(url_grupo, language="http")

# --- VISÃO 7: ADMINISTRAÇÃO GERAL ---
elif modo == "👑 Administração Geral":
    st.header("👑 Administração Global (SuperAdmin)")
    
    col_admin1, col_admin2 = st.columns(2)

    with col_admin1:
        st.subheader("🏢 Cadastrar / Editar Grupos & Imagens")
        with st.form("form_novo_grupo"):
            novo_grupo_nome = st.text_input("Nome do Grupo / Ministério")
            nova_img_url = st.text_input("URL da Imagem (Link)", value="https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80")
            
            if st.form_submit_button("Salvar Grupo / Imagem"):
                if novo_grupo_nome.strip():
                    nome_formatado = novo_grupo_nome.strip()
                    mask_grp = df_grupos["Grupo_ID"] == nome_formatado
                    if mask_grp.any():
                        df_grupos.loc[mask_grp, "Imagem_URL"] = nova_img_url.strip()
                        st.success(f"Imagem do '{nome_formatado}' atualizada!")
                    else:
                        df_grupos = pd.concat([df_grupos, pd.DataFrame([{"Grupo_ID": nome_formatado, "Imagem_URL": nova_img_url.strip()}])], ignore_index=True)
                        st.success(f"Grupo '{nome_formatado}' cadastrado!")
                    
                    salvar_df(df_grupos, ARQUIVO_GRUPOS)
                    st.rerun()

        st.write("**Grupos Cadastrados:**")
        st.dataframe(df_grupos, use_container_width=True, hide_index=True)

    with col_admin2:
        st.subheader("👥 Cadastrar Gestores das Cantinas")
        df_usr = carregar_df(ARQUIVO_USUARIOS)
        
        with st.form("form_novo_usuario"):
            novo_usr = st.text_input("Usuário")
            nova_pwd = st.text_input("Senha")
            nova_role = st.selectbox("Papel", ["Gestor", "SuperAdmin"])
            novo_grp_usr = st.selectbox("Pertence ao Grupo:", ["TODOS"] + lista_de_grupos)

            if st.form_submit_button("Cadastrar Gestor"):
                if novo_usr and nova_pwd:
                    u_dict = {"Usuario": novo_usr.strip(), "Senha": nova_pwd.strip(), "Role": nova_role, "Grupo_ID": novo_grp_usr}
                    salvar_df(pd.concat([df_usr, pd.DataFrame([u_dict])], ignore_index=True), ARQUIVO_USUARIOS)
                    st.success("Gestor cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha usuário e senha.")

        st.write("**Gestores Cadastrados:**")
        st.dataframe(df_usr[["Usuario", "Role", "Grupo_ID"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Faturamento Consolidado de Todos os Ministérios")
    df_vendas = carregar_df(ARQUIVO_VENDAS)
    if not df_vendas.empty:
        resumo = df_vendas.groupby("Grupo_ID")["Valor_Total"].agg(["sum", "count"]).rename(columns={"sum": "Faturamento (R$)", "count": "Qtd Vendas"})
        st.dataframe(resumo, use_container_width=True)import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Cantina dos Ministérios", page_icon="🍔", layout="wide")

# Arquivos de dados
ARQUIVO_GRUPOS = "grupos.csv"
ARQUIVO_ESTOQUE = "estoque_cantina.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"
ARQUIVO_USUARIOS = "usuarios.csv"

URL_BASE = "https://cantina-mp-bypacheco.streamlit.app/"

# Lista de Ministérios com Ilustrações e Temática Cristã
GRUPOS_PADRAO = [
    {"Grupo_ID": "Min. da Família", "Imagem_URL": "data:image/jpeg;base64,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"},
    {"Grupo_ID": "Min. de Jovens", "Imagem_URL": "data:image/jpeg;base64,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"},
    {"Grupo_ID": "Min. Cura e Libertação", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtZRL3MZA6TUH3A2o9jSkaL6r-rtIitiRPpxTqbzgztQ&s"},
    {"Grupo_ID": "Min. de Empresários", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdjSmHnOSVida6x0NkR52DBThNAwHFtFRzEyNBfETjdg&s=10"},
    {"Grupo_ID": "Min. de Homens", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJNAwYSmSj3SXMO4-K9vruToQWwDnmfV2Fea3n1jt8lA&s=10"},
    {"Grupo_ID": "Min. das Mulheres", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGrlB19ghAbOSaKMDVaFJuLWAMRUQhRHdaf62Ivx4dFA&s=10"},
    {"Grupo_ID": "Min. da Melhor idade", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ19SW2RwQPT8CfgEYXH5UwfnaLQOfuPhE7hta8jspqFg&s=10"},
    {"Grupo_ID": "Min. de Juniores", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSA_Fd7xyuLuag7dT5UrAUAtPgpqT5jcqAx8lsF_pSkww&s=10"},
    {"Grupo_ID": "Min. das Crianças", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKS4yP2yvabRh1e9gn0EOuwbyopZa0K71k5aqLPscldA&s=10"},
    {"Grupo_ID": "Instruir Para Crescer", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT9QfMCQSkRmiypRxyuAJtI679tP1yetVqsDueU1zibJg&s=10"},
    {"Grupo_ID": "Min. de Dança", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTot1EkRROx7zmUsn4_B6wC6kSVzlDQMHRUojyMIQu9sQ&s=10"},
    {"Grupo_ID": "Min. de Louvor", "Imagem_URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTq_6iq7oqbRXBDCH4AvmPJGmYEyamUflv-5itvcQzDbQ&s=10"},
]

# --- INICIALIZAÇÃO SEGURA DOS DADOS ---

def inicializar_arquivos():
    # Sobrescreve/Atualiza o CSV com as novas imagens temáticas cristãs
    pd.DataFrame(GRUPOS_PADRAO).to_csv(ARQUIVO_GRUPOS, index=False)

    if not os.path.exists(ARQUIVO_USUARIOS):
        df_usr = pd.DataFrame([
            {"Usuario": "admin", "Senha": "123", "Role": "SuperAdmin", "Grupo_ID": "TODOS"}
        ])
        df_usr.to_csv(ARQUIVO_USUARIOS, index=False)

    if not os.path.exists(ARQUIVO_ESTOQUE) or os.path.getsize(ARQUIVO_ESTOQUE) == 0:
        pd.DataFrame(columns=["Grupo_ID", "Produto", "Estoque", "Minimo_Recomendado", "Preco"]).to_csv(ARQUIVO_ESTOQUE, index=False)

    if not os.path.exists(ARQUIVO_VENDAS) or os.path.getsize(ARQUIVO_VENDAS) == 0:
        pd.DataFrame(columns=["Grupo_ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento"]).to_csv(ARQUIVO_VENDAS, index=False)

    if not os.path.exists(ARQUIVO_PEDIDOS) or os.path.getsize(ARQUIVO_PEDIDOS) == 0:
        pd.DataFrame(columns=["ID", "Grupo_ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"]).to_csv(ARQUIVO_PEDIDOS, index=False)

inicializar_arquivos()

# --- FUNÇÕES AUXILIARES ---

def carregar_df(caminho):
    return pd.read_csv(caminho) if os.path.exists(caminho) else pd.DataFrame()

def salvar_df(df, caminho):
    df.to_csv(caminho, index=False)

def gerar_qrcode(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- SESSÃO E AUTENTICAÇÃO ---

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state.role = "Cliente"
    st.session_state.grupo_id = None

st.sidebar.title("🔐 Login de Gestão")

df_usuarios = carregar_df(ARQUIVO_USUARIOS)

if st.session_state.usuario_logado is None:
    with st.sidebar.expander("Acesso para Gestores e Admin", expanded=False):
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            usr_match = df_usuarios[(df_usuarios["Usuario"] == user_input.strip()) & (df_usuarios["Senha"] == pass_input.strip())]
            if not usr_match.empty:
                info_usr = usr_match.iloc[0]
                st.session_state.usuario_logado = info_usr["Usuario"]
                st.session_state.role = info_usr["Role"]
                st.session_state.grupo_id = info_usr["Grupo_ID"]
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha inválidos.")
else:
    st.sidebar.info(f"👤 **{st.session_state.usuario_logado}** ({st.session_state.role})")
    if st.button("Sair (Logout)"):
        st.session_state.usuario_logado = None
        st.session_state.role = "Cliente"
        st.session_state.grupo_id = None
        st.rerun()

st.title("🍔 CANTINA MP - GETSEMANI")

# --- TRATAMENTO DOS DADOS ---

df_grupos = carregar_df(ARQUIVO_GRUPOS)
df_estoque = carregar_df(ARQUIVO_ESTOQUE)
df_pedidos = carregar_df(ARQUIVO_PEDIDOS)

if "Imagem_URL" not in df_grupos.columns:
    df_grupos["Imagem_URL"] = "https://img.freepik.com/vetores-gratis/biblia-aberta-com-luz-saindo-e-arvore-crescendo-ensino_23-2149150055.jpg?w=800"
    salvar_df(df_grupos, ARQUIVO_GRUPOS)

if "Grupo_ID" not in df_estoque.columns:
    df_estoque = pd.DataFrame(columns=["Grupo_ID", "Produto", "Estoque", "Minimo_Recomendado", "Preco"])
    salvar_df(df_estoque, ARQUIVO_ESTOQUE)

if "Grupo_ID" not in df_pedidos.columns:
    df_pedidos = pd.DataFrame(columns=["ID", "Grupo_ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"])
    salvar_df(df_pedidos, ARQUIVO_PEDIDOS)

lista_de_grupos = df_grupos["Grupo_ID"].tolist() if not df_grupos.empty else []

if st.session_state.role == "SuperAdmin":
    st.sidebar.subheader("👑 Painel Admin")
    grupo_ativo = st.sidebar.selectbox("Visualizar Dados do Grupo:", ["TODOS"] + lista_de_grupos)
elif st.session_state.role == "Gestor":
    grupo_ativo = st.session_state.grupo_id
    st.sidebar.info(f"Sua Cantina: **{grupo_ativo}**")
else:
    query_params = st.query_params
    grupo_param = query_params.get("grupo", None)
    
    if grupo_param and grupo_param in lista_de_grupos:
        grupo_ativo = grupo_param
    else:
        grupo_ativo = st.sidebar.selectbox("Escolha o Ministério / Grupo:", lista_de_grupos)

# --- NAVEGAÇÃO COMPATÍVEL ---
opcoes_menu = ["📱 Cardápio (Cliente)"]
if st.session_state.role in ["Gestor", "SuperAdmin"]:
    opcoes_menu.extend(["🔔 Pedidos Recebidos", "🛒 Venda Balcão", "⚙️ Gestão de Estoque", "📊 Histórico de Vendas", "📲 Gerar QR Code"])
if st.session_state.role == "SuperAdmin":
    opcoes_menu.append("👑 Administração Geral")

modo = st.sidebar.radio("Navegação do App:", opcoes_menu, horizontal=True)
st.divider()

# --- VISÃO 1: CARDÁPIO DO CLIENTE ---
if modo == "📱 Cardápio (Cliente)":
    if grupo_ativo != "TODOS":
        info_grupo = df_grupos[df_grupos["Grupo_ID"] == grupo_ativo]
        url_imagem = info_grupo["Imagem_URL"].values[0] if not info_grupo.empty else "https://img.freepik.com/vetores-gratis/biblia-aberta-com-luz-saindo-e-arvore-crescendo-ensino_23-2149150055.jpg?w=800"
        
        col_img, col_tit = st.columns([1, 3])
        with col_img:
            st.image(url_imagem, use_container_width=True)
        with col_tit:
            st.title(f"✨ {grupo_ativo}")
            st.subheader("Cardápio Digital da Cantina")
            st.caption("Faça seu pedido abaixo para ser preparado pela equipe.")
    else:
        st.header("📱 Cardápio Digital - Visão Geral")

    df_estoque_grp = df_estoque[df_estoque["Grupo_ID"] == grupo_ativo] if not df_estoque.empty else pd.DataFrame()
    df_pedidos_grp = df_pedidos[(df_pedidos["Grupo_ID"] == grupo_ativo) & (df_pedidos["Status"] == "Pendente")] if not df_pedidos.empty else pd.DataFrame()

    if df_estoque_grp.empty:
        st.warning(f"Nenhum produto cadastrado para a cantina **{grupo_ativo}** no momento.")
    else:
        reservas = df_pedidos_grp.groupby("Produto")["Quantidade"].sum().to_dict() if not df_pedidos_grp.empty else {}
        
        df_cardapio = df_estoque_grp.copy()
        df_cardapio["Estoque_Reservado"] = df_cardapio["Produto"].map(reservas).fillna(0).astype(int)
        df_cardapio["Estoque_Disponivel"] = df_cardapio["Estoque"] - df_cardapio["Estoque_Reservado"]
        
        df_disp = df_cardapio[df_cardapio["Estoque_Disponivel"] > 0]

        if df_disp.empty:
            st.error("⚠️ Todos os produtos desta cantina estão esgotados agora!")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form("form_cliente", clear_on_submit=True):
                    nome_cliente = st.text_input("Seu Nome *")
                    celular = st.text_input("Celular / WhatsApp *")
                    prod_sel = st.selectbox("Produto", df_disp["Produto"].tolist())
                    
                    linha_prod = df_disp[df_disp["Produto"] == prod_sel].iloc[0]
                    qtd_max = int(linha_prod["Estoque_Disponivel"])
                    preco_unit = float(linha_prod["Preco"])

                    qtd = st.number_input(f"Quantidade (Max: {qtd_max})", min_value=1, max_value=max(1, qtd_max), value=1)
                    pagto = st.radio("Pagamento", ["Pix", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Posterior"])

                    total = qtd * preco_unit
                    st.info(f"**Total:** R$ {total:.2f}")

                    if st.form_submit_button("🚀 Enviar Pedido", type="primary", use_container_width=True):
                        if not nome_cliente.strip() or not celular.strip():
                            st.warning("Preencha seu nome e celular.")
                        else:
                            novo_pedido = {
                                "ID": int(datetime.now().timestamp()),
                                "Grupo_ID": grupo_ativo,
                                "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Cliente": f"{nome_cliente.strip()} ({celular.strip()})",
                                "Produto": prod_sel,
                                "Quantidade": qtd,
                                "Valor_Total": round(total, 2),
                                "Forma_Pagamento": pagto,
                                "Status": "Pendente"
                            }
                            salvar_df(pd.concat([df_pedidos, pd.DataFrame([novo_pedido])], ignore_index=True), ARQUIVO_PEDIDOS)
                            st.balloons()
                            st.success("✅ Pedido enviado! Aguarde no balcão.")

            with col2:
                st.subheader("Itens Disponíveis")
                st.dataframe(df_disp[["Produto", "Preco", "Estoque_Disponivel"]].rename(columns={"Preco": "Preço (R$)", "Estoque_Disponivel": "Disponível"}), use_container_width=True, hide_index=True)

# --- VISÃO 2: PEDIDOS RECEBIDOS ---
elif modo == "🔔 Pedidos Recebidos":
    st.header(f"🔔 Pedidos Recebidos - {grupo_ativo}")
    df_vendas = carregar_df(ARQUIVO_VENDAS)

    filtro_pedidos = df_pedidos if grupo_ativo == "TODOS" else df_pedidos[df_pedidos["Grupo_ID"] == grupo_ativo]
    pendentes = filtro_pedidos[filtro_pedidos["Status"] == "Pendente"] if not filtro_pedidos.empty else pd.DataFrame()

    if pendentes.empty:
        st.info("Nenhum pedido pendente.")
    else:
        for idx, ped in pendentes.iterrows():
            with st.expander(f"📦 [{ped['Grupo_ID']}] {ped['Cliente']} - R$ {ped['Valor_Total']:.2f}", expanded=True):
                st.write(f"**Item:** {ped['Quantidade']}x {ped['Produto']} | **Pagamento:** {ped['Forma_Pagamento']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar", key=f"conf_{ped['ID']}", type="primary"):
                        mask = (df_estoque["Grupo_ID"] == ped["Grupo_ID"]) & (df_estoque["Produto"] == ped["Produto"])
                        if not df_estoque[mask].empty and df_estoque.loc[mask, "Estoque"].values[0] >= ped["Quantidade"]:
                            df_estoque.loc[mask, "Estoque"] -= ped["Quantidade"]
                            salvar_df(df_estoque, ARQUIVO_ESTOQUE)

                            nova_venda = ped.to_dict()
                            del nova_venda["ID"]
                            del nova_venda["Status"]
                            salvar_df(pd.concat([df_vendas, pd.DataFrame([nova_venda])], ignore_index=True), ARQUIVO_VENDAS)

                            df_pedidos.loc[df_pedidos["ID"] == ped["ID"], "Status"] = "Aprovado"
                            salvar_df(df_pedidos, ARQUIVO_PEDIDOS)
                            st.success("Aprovado!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente!")
                with col2:
                    if st.button("❌ Rejeitar", key=f"rej_{ped['ID']}"):
                        df_pedidos.loc[df_pedidos["ID"] == ped["ID"], "Status"] = "Rejeitado"
                        salvar_df(df_pedidos, ARQUIVO_PEDIDOS)
                        st.warning("Rejeitado.")
                        st.rerun()

# --- VISÃO 3: VENDAS BALCÃO ---
elif modo == "🛒 Venda Balcão":
    st.header(f"🛒 Venda Balcão - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        df_vendas = carregar_df(ARQUIVO_VENDAS)
        df_est_grp = df_estoque[df_estoque["Grupo_ID"] == grupo_ativo] if not df_estoque.empty else pd.DataFrame()

        if df_est_grp.empty:
            st.warning("Nenhum produto cadastrado.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                prod_sel = st.selectbox("Produto", df_est_grp["Produto"].tolist())
                linha_prod = df_est_grp[df_est_grp["Produto"] == prod_sel].iloc[0]
                qtd_est = int(linha_prod["Estoque"])
                preco = float(linha_prod["Preco"])

                qtd = st.number_input("Quantidade", min_value=1, max_value=max(1, qtd_est), value=1)
                pagto = st.radio("Pagamento", ["Pix", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Posterior"])
                total = qtd * preco
                st.info(f"**Total:** R$ {total:.2f}")

                if st.button("Confirmar Venda", type="primary"):
                    if qtd_est >= qtd:
                        mask = (df_estoque["Grupo_ID"] == grupo_ativo) & (df_estoque["Produto"] == prod_sel)
                        df_estoque.loc[mask, "Estoque"] -= qtd
                        salvar_df(df_estoque, ARQUIVO_ESTOQUE)
                        venda_dict = {
                            "Grupo_ID": grupo_ativo, "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Cliente": "Venda Balcão", "Produto": prod_sel, "Quantidade": qtd,
                            "Valor_Total": round(total, 2), "Forma_Pagamento": pagto
                        }
                        salvar_df(pd.concat([df_vendas, pd.DataFrame([venda_dict])], ignore_index=True), ARQUIVO_VENDAS)
                        st.success("Venda registrada!")
                        st.rerun()

            with col2:
                st.subheader("Estoque Local")
                st.dataframe(df_est_grp[["Produto", "Estoque", "Preco"]], use_container_width=True)

# --- VISÃO 4: GESTÃO DE ESTOQUE ---
elif modo == "⚙️ Gestão de Estoque":
    st.header(f"⚙️ Gestão de Estoque - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        with st.form("form_prod"):
            nome = st.text_input("Nome do Produto")
            qtd = st.number_input("Estoque", min_value=0, value=10)
            minimo = st.number_input("Estoque Mínimo", min_value=0, value=5)
            preco = st.number_input("Preço (R$)", min_value=0.0, value=5.00)

            if st.form_submit_button("Salvar / Atualizar Produto"):
                if nome.strip():
                    nome_limpo = nome.strip().capitalize()
                    mask = (df_estoque["Grupo_ID"] == grupo_ativo) & (df_estoque["Produto"] == nome_limpo)
                    if not df_estoque[mask].empty:
                        df_estoque.loc[mask, ["Estoque", "Minimo_Recomendado", "Preco"]] = [qtd, minimo, preco]
                    else:
                        nova_linha = {"Grupo_ID": grupo_ativo, "Produto": nome_limpo, "Estoque": qtd, "Minimo_Recomendado": minimo, "Preco": preco}
                        df_estoque = pd.concat([df_estoque, pd.DataFrame([nova_linha])], ignore_index=True)
                    salvar_df(df_estoque, ARQUIVO_ESTOQUE)
                    st.success("Produto salvo!")
                    st.rerun()

        st.dataframe(df_estoque[df_estoque["Grupo_ID"] == grupo_ativo], use_container_width=True)

# --- VISÃO 5: HISTÓRICO ---
elif modo == "📊 Histórico de Vendas":
    st.header(f"📊 Histórico de Vendas - {grupo_ativo}")
    df_vendas = carregar_df(ARQUIVO_VENDAS)
    filtro_vendas = df_vendas if grupo_ativo == "TODOS" else df_vendas[df_vendas["Grupo_ID"] == grupo_ativo]

    if not filtro_vendas.empty:
        st.metric("Faturamento Total", f"R$ {filtro_vendas['Valor_Total'].sum():.2f}")
        st.dataframe(filtro_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda cadastrada.")

# --- VISÃO 6: QR CODE ---
elif modo == "📲 Gerar QR Code":
    st.header(f"📲 QR Code - {grupo_ativo}")
    if grupo_ativo == "TODOS":
        st.warning("Selecione um grupo específico na barra lateral.")
    else:
        url_grupo = f"{URL_BASE}?grupo={grupo_ativo}"
        qr_bytes = gerar_qrcode(url_grupo)
        st.image(qr_bytes, width=250)
        st.code(url_grupo, language="http")

# --- VISÃO 7: ADMINISTRAÇÃO GERAL ---
elif modo == "👑 Administração Geral":
    st.header("👑 Administração Global (SuperAdmin)")
    
    col_admin1, col_admin2 = st.columns(2)

    with col_admin1:
        st.subheader("🏢 Cadastrar / Editar Grupos & Imagens")
        with st.form("form_novo_grupo"):
            novo_grupo_nome = st.text_input("Nome do Grupo / Ministério")
            nova_img_url = st.text_input("URL da Imagem (Link)", value="https://img.freepik.com/vetores-gratis/biblia-aberta-com-luz-saindo-e-arvore-crescendo-ensino_23-2149150055.jpg?w=800")
            
            if st.form_submit_button("Salvar Grupo / Imagem"):
                if novo_grupo_nome.strip():
                    nome_formatado = novo_grupo_nome.strip()
                    mask_grp = df_grupos["Grupo_ID"] == nome_formatado
                    if mask_grp.any():
                        df_grupos.loc[mask_grp, "Imagem_URL"] = nova_img_url.strip()
                        st.success(f"Imagem do '{nome_formatado}' atualizada!")
                    else:
                        df_grupos = pd.concat([df_grupos, pd.DataFrame([{"Grupo_ID": nome_formatado, "Imagem_URL": nova_img_url.strip()}])], ignore_index=True)
                        st.success(f"Grupo '{nome_formatado}' cadastrado!")
                    
                    salvar_df(df_grupos, ARQUIVO_GRUPOS)
                    st.rerun()

        st.write("**Grupos Cadastrados:**")
        st.dataframe(df_grupos, use_container_width=True, hide_index=True)

    with col_admin2:
        st.subheader("👥 Cadastrar Gestores das Cantinas")
        df_usr = carregar_df(ARQUIVO_USUARIOS)
        
        with st.form("form_novo_usuario"):
            novo_usr = st.text_input("Usuário")
            nova_pwd = st.text_input("Senha")
            nova_role = st.selectbox("Papel", ["Gestor", "SuperAdmin"])
            novo_grp_usr = st.selectbox("Pertence ao Grupo:", ["TODOS"] + lista_de_grupos)

            if st.form_submit_button("Cadastrar Gestor"):
                if novo_usr and nova_pwd:
                    u_dict = {"Usuario": novo_usr.strip(), "Senha": nova_pwd.strip(), "Role": nova_role, "Grupo_ID": novo_grp_usr}
                    salvar_df(pd.concat([df_usr, pd.DataFrame([u_dict])], ignore_index=True), ARQUIVO_USUARIOS)
                    st.success("Gestor cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha usuário e senha.")

        st.write("**Gestores Cadastrados:**")
        st.dataframe(df_usr[["Usuario", "Role", "Grupo_ID"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Faturamento Consolidado de Todos os Ministérios")
    df_vendas = carregar_df(ARQUIVO_VENDAS)
    if not df_vendas.empty:
        resumo = df_vendas.groupby("Grupo_ID")["Valor_Total"].agg(["sum", "count"]).rename(columns={"sum": "Faturamento (R$)", "count": "Qtd Vendas"})
        st.dataframe(resumo, use_container_width=True)
