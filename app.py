import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Cantina - Pedidos e Estoque", page_icon="🍔", layout="wide")

ARQUIVO_ESTOQUE = "estoque_cantina.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_PEDIDOS = "pedidos_pendentes.csv"

# SENHA DE ACESSO DO GESTOR
SENHA_GESTOR = "1234"  # <-- Altere aqui para a senha que desejar!

# --- FUNÇÕES DE DADOS ---
def carregar_estoque():
    if os.path.exists(ARQUIVO_ESTOQUE):
        df = pd.read_csv(ARQUIVO_ESTOQUE)
        if "Preco" not in df.columns:
            df["Preco"] = 0.0
        return df
    else:
        df = pd.DataFrame({
            "Produto": ["Salgado", "Refrigerante", "Suco", "Chocolate", "Sanduíche"],
            "Estoque": [50, 40, 5, 60, 2],
            "Minimo_Recomendado": [10, 10, 8, 15, 5],
            "Preco": [6.50, 5.00, 4.50, 3.50, 8.00]
        })
        df.to_csv(ARQUIVO_ESTOQUE, index=False)
        return df

def carregar_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        return pd.read_csv(ARQUIVO_VENDAS)
    else:
        df = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento"])
        df.to_csv(ARQUIVO_VENDAS, index=False)
        return df

def carregar_pedidos():
    if os.path.exists(ARQUIVO_PEDIDOS):
        return pd.read_csv(ARQUIVO_PEDIDOS)
    else:
        df = pd.DataFrame(columns=["ID", "Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento", "Status"])
        df.to_csv(ARQUIVO_PEDIDOS, index=False)
        return df

def salvar_estoque(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def salvar_pedido_pendente(registro):
    df_pedidos = carregar_pedidos()
    df_novo = pd.DataFrame([registro])
    df_pedidos = pd.concat([df_pedidos, df_novo], ignore_index=True)
    df_pedidos.to_csv(ARQUIVO_PEDIDOS, index=False)

def salvar_venda_confirmada(registro):
    df_vendas = carregar_vendas()
    df_novo = pd.DataFrame([registro])
    df_vendas = pd.concat([df_vendas, df_novo], ignore_index=True)
    df_vendas.to_csv(ARQUIVO_VENDAS, index=False)

def atualizar_pedidos_pendentes(df_pedidos):
    df_pedidos.to_csv(ARQUIVO_PEDIDOS, index=False)

def limpar_vendas():
    df_vazio = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Valor_Total", "Forma_Pagamento"])
    df_vazio.to_csv(ARQUIVO_VENDAS, index=False)

# Inicializa sessão
if "df" not in st.session_state:
    st.session_state.df = carregar_estoque()

st.title("🍔 Gestão da Cantina e Pedidos Online")

# Menu na barra lateral (Sidebar)
modo = st.sidebar.radio("Selecione o Acesso:", ["📱 Área do Cliente (Cardápio)", "🔒 Área Restrita (Cantina)"])

# --- VISÃO DO CLIENTE ---
if modo == "📱 Área do Cliente (Cardápio)":
    st.header("📱 Cardápio Digital - Faça seu Pedido")
    
    if st.session_state.df.empty:
        st.warning("Nenhum produto disponível no momento.")
    else:
        col_c1, col_c2 = st.columns([1, 1])

        with col_c1:
            nome_cliente = st.text_input("Seu Nome", placeholder="Ex: João Silva")
            mesa_ou_local = st.text_input("Mesa / Local de Entrega", placeholder="Ex: Mesa 04")
            
            produtos_disponiveis = st.session_state.df[st.session_state.df["Estoque"] > 0]["Produto"].tolist()

            if not produtos_disponiveis:
                st.error("Desculpe, todos os produtos estão esgotados!")
            else:
                produto_pedid = st.selectbox("Selecione o Produto", produtos_disponiveis, key="cli_prod")
                linha_prod = st.session_state.df[st.session_state.df["Produto"] == produto_pedid].iloc[0]
                
                qtd_max = int(linha_prod["Estoque"])
                preco_unit = float(linha_prod.get("Preco", 0.0))

                qtd_pedida = st.number_input("Quantidade", min_value=1, max_value=qtd_max, value=1, key="cli_qtd")
                forma_pagto = st.radio("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Débito", "Cartão de Crédito"], key="cli_pagto")

                total_pedido = qtd_pedida * preco_unit
                st.success(f"**Total a pagar:** R$ {total_pedido:.2f}")

                if st.button("🚀 Enviar Pedido", type="primary", use_container_width=True):
                    if not nome_cliente.strip():
                        st.warning("Por favor, digite seu nome antes de enviar.")
                    else:
                        identificacao = f"{nome_cliente.strip()} ({mesa_ou_local.strip()})" if mesa_ou_local.strip() else nome_cliente.strip()
                        novo_id = int(datetime.now().timestamp())
                        registro = {
                            "ID": novo_id,
                            "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Cliente": identificacao,
                            "Produto": produto_pedid,
                            "Quantidade": qtd_pedida,
                            "Valor_Total": round(total_pedido, 2),
                            "Forma_Pagamento": forma_pagto,
                            "Status": "Pendente"
                        }
                        salvar_pedido_pendente(registro)
                        st.balloons()
                        st.success("✅ Pedido enviado com sucesso! Aguarde a confirmação da cantina.")

        with col_c2:
            st.subheader("Cardápio")
            st.dataframe(
                st.session_state.df[["Produto", "Preco"]].rename(columns={"Preco": "Preço (R$)"}),
                use_container_width=True
            )

# --- VISÃO DA CANTINA (COM SENHA) ---
else:
    st.sidebar.divider()
    senha_digitada = st.sidebar.text_input("Digite a Senha do Gestor:", type="password")

    if senha_digitada == SENHA_GESTOR:
        # Alerta de estoque crítico
        produtos_baixos = st.session_state.df[st.session_state.df["Estoque"] <= st.session_state.df["Minimo_Recomendado"]]
        if not produtos_baixos.empty:
            lista_alertas = ", ".join([f"**{row['Produto']}** ({row['Estoque']} un / mín {row['Minimo_Recomendado']})" for _, row in produtos_baixos.iterrows()])
            st.error(f"🚨 **ATENÇÃO! ESTOQUE CRÍTICO / MÍNIMO:** {lista_alertas}", icon="⚠️")

        aba_aprovacao, aba_balcao, aba_gestao, aba_historico = st.tabs([
            "🔔 Pedidos Recebidos",
            "🛒 Venda Balcão",
            "⚙️ Gestão de Estoque",
            "📊 Histórico de Vendas"
        ])

        with aba_aprovacao:
            st.header("🔔 Pedidos Recebidos")
            if st.button("🔄 Atualizar Pedidos"):
                st.rerun()

            df_pedidos = carregar_pedidos()
            pedidos_pendentes = df_pedidos[df_pedidos["Status"] == "Pendente"]

            if pedidos_pendentes.empty:
                st.info("Nenhum pedido pendente no momento.")
            else:
                for idx, pedido in pedidos_pendentes.iterrows():
                    with st.expander(f"📦 Pedido de **{pedido['Cliente']}** - R$ {pedido['Valor_Total']:.2f} ({pedido['Data_Hora']})", expanded=True):
                        col_info, col_b1, col_b2 = st.columns([3, 1, 1])

                        with col_info:
                            st.write(f"**Produto:** {pedido['Quantidade']}x {pedido['Produto']}")
                            st.write(f"**Pagamento:** {pedido['Forma_Pagamento']}")

                        with col_b1:
                            if st.button("✅ Confirmar", key=f"conf_{pedido['ID']}", type="primary"):
                                estoque_atual = st.session_state.df.loc[st.session_state.df["Produto"] == pedido["Produto"], "Estoque"].values[0]
                                if estoque_atual >= pedido["Quantidade"]:
                                    st.session_state.df.loc[st.session_state.df["Produto"] == pedido["Produto"], "Estoque"] -= pedido["Quantidade"]
                                    salvar_estoque(st.session_state.df)

                                    salvar_venda_confirmada({
                                        "Data_Hora": pedido["Data_Hora"],
                                        "Cliente": pedido["Cliente"],
                                        "Produto": pedido["Produto"],
                                        "Quantidade": pedido["Quantidade"],
                                        "Valor_Total": pedido["Valor_Total"],
                                        "Forma_Pagamento": pedido["Forma_Pagamento"]
                                    })

                                    df_pedidos.loc[df_pedidos["ID"] == pedido["ID"], "Status"] = "Aprovado"
                                    atualizar_pedidos_pendentes(df_pedidos)

                                    st.success("Pedido confirmado!")
                                    st.rerun()
                                else:
                                    st.error("Estoque insuficiente!")

                        with col_b2:
                            if st.button("❌ Rejeitar", key=f"rej_{pedido['ID']}"):
                                df_pedidos.loc[df_pedidos["ID"] == pedido["ID"], "Status"] = "Rejeitado"
                                atualizar_pedidos_pendentes(df_pedidos)
                                st.warning("Pedido rejeitado.")
                                st.rerun()

        with aba_balcao:
            st.header("Venda Balcão")
            col1, col2 = st.columns([1, 2])
            with col1:
                produtos_disponiveis = st.session_state.df["Produto"].tolist()
                produto_selecionado = st.selectbox("Selecione o Produto", produtos_disponiveis, key="balcao_prod")
                
                linha_prod = st.session_state.df[st.session_state.df["Produto"] == produto_selecionado].iloc[0]
                qtd_atual = int(linha_prod["Estoque"])
                preco_unitario = float(linha_prod.get("Preco", 0.0))
                
                qtd_saida = st.number_input("Quantidade", min_value=1, max_value=qtd_atual if qtd_atual > 0 else 1, value=1, key="balcao_qtd")
                forma_pagamento = st.radio("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Débito", "Cartão de Crédito"], horizontal=True, key="balcao_pagto")
                
                valor_total = qtd_saida * preco_unitario
                st.info(f"**Total:** R$ {valor_total:.2f}")
                
                if st.button("Confirmar Venda", type="primary", use_container_width=True):
                    if qtd_atual >= qtd_saida:
                        st.session_state.df.loc[st.session_state.df["Produto"] == produto_selecionado, "Estoque"] -= qtd_saida
                        salvar_estoque(st.session_state.df)
                        
                        salvar_venda_confirmada({
                            "Data_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Cliente": "Venda no Balcão",
                            "Produto": produto_selecionado,
                            "Quantidade": qtd_saida,
                            "Valor_Total": round(valor_total, 2),
                            "Forma_Pagamento": forma_pagamento
                        })
                        st.success("Venda registrada!")
                        st.rerun()

            with col2:
                st.dataframe(st.session_state.df, use_container_width=True)

        with aba_gestao:
            st.header("Gestão de Estoque")
            col_cad, col_exc = st.columns([2, 1])
            with col_cad:
                with st.form("form_produto"):
                    novo_nome = st.text_input("Nome do Produto")
                    nova_qtd = st.number_input("Quantidade em Estoque", min_value=0, value=10)
                    novo_min = st.number_input("Estoque Mínimo", min_value=0, value=5)
                    novo_preco = st.number_input("Preço (R$)", min_value=0.0, value=5.00, step=0.50)
                        
                    if st.form_submit_button("Salvar Produto"):
                        if novo_nome.strip() != "":
                            nome_limpo = novo_nome.strip().capitalize()
                            if nome_limpo in st.session_state.df["Produto"].values:
                                st.session_state.df.loc[st.session_state.df["Produto"] == nome_limpo, "Estoque"] = nova_qtd
                                st.session_state.df.loc[st.session_state.df["Produto"] == nome_limpo, "Minimo_Recomendado"] = novo_min
                                st.session_state.df.loc[st.session_state.df["Produto"] == nome_limpo, "Preco"] = novo_preco
                            else:
                                nova_linha = pd.DataFrame([{"Produto": nome_limpo, "Estoque": nova_qtd, "Minimo_Recomendado": novo_min, "Preco": novo_preco}])
                                st.session_state.df = pd.concat([st.session_state.df, nova_linha], ignore_index=True)
                            
                            salvar_estoque(st.session_state.df)
                            st.success("Salvo!")
                            st.rerun()

            with col_exc:
                if not st.session_state.df.empty:
                    prod_para_excluir = st.selectbox("Excluir Produto", st.session_state.df["Produto"].tolist(), key="exc_prod")
                    confirmar = st.checkbox("Confirmar Exclusão")
                    if st.button("🗑️ Excluir"):
                        if confirmar:
                            st.session_state.df = st.session_state.df[st.session_state.df["Produto"] != prod_para_excluir].reset_index(drop=True)
                            salvar_estoque(st.session_state.df)
                            st.rerun()

            st.dataframe(st.session_state.df, use_container_width=True)

        with aba_historico:
            st.header("Histórico de Vendas")
            df_vendas = carregar_vendas()
            if not df_vendas.empty:
                st.metric("Faturamento Total", f"R$ {df_vendas['Valor_Total'].sum():.2f}")
                st.dataframe(df_vendas.sort_index(ascending=False), use_container_width=True)
                
                if st.button("Limpar Histórico") and st.checkbox("Confirmar limpeza"):
                    limpar_vendas()
                    st.rerun()
            else:
                st.info("Sem vendas registradas.")
    else:
        st.warning("🔒 Digite a senha na barra lateral para acessar o painel administrativo.")
