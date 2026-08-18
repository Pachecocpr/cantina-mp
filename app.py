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
        "Imagem_URL": "https://images.unsplash.com/photo-1544027993-37dbfe43562a?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Jovens", 
        "Imagem_URL": "https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. Cura e Libertação", 
        "Imagem_URL": "https://images.unsplash.com/photo-1507692049790-de58290a4334?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Empresários", 
        "Imagem_URL": "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Homens", 
        "Imagem_URL": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. das Mulheres", 
        "Imagem_URL": "https://images.unsplash.com/photo-1515162305285-0293e4767cc2?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. da Melhor idade", 
        "Imagem_URL": "https://images.unsplash.com/photo-1516307365426-bea591f05011?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Juniores", 
        "Imagem_URL": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. das Crianças", 
        "Imagem_URL": "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Instruir Para Crescer", 
        "Imagem_URL": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Dança", 
        "Imagem_URL": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=800&q=80"
    },
    {
        "Grupo_ID": "Min. de Louvor", 
        "Imagem_URL": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80"
    },
]

# --- INICIALIZAÇÃO DE DADOS E CRIAÇÃO DO ADMIN ---

def inicializar_arquivos():
    pd.DataFrame(GRUPOS_PADRAO).to_csv(ARQUIVO_GRUPOS, index=False)

    df_usr_padrao = pd.DataFrame([
        {"Usuario": "admin", "Senha": "123", "Role": "SuperAdmin", "Grupo_ID": "TODOS"}
    ])
    
    if not os.path.exists(ARQUIVO_USUARIOS) or os.path.getsize(ARQUIVO_USUARIOS) == 0:
        df_usr_padrao.to_csv(ARQUIVO_USUARIOS, index=False)
    else:
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
        st.dataframe(resumo, use_container_width=True)
