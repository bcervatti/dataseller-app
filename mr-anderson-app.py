# Para rodar este app, use o terminal com:
# streamlit run mr-anderson-app.py

import os
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st # type: ignore
import tempfile
import zipfile
import io
from datetime import datetime

st.set_page_config(page_title="DATA SELLER v1.2 | Amplie suas vendas e fortaleça sua comunidade", layout="wide")
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">

    <style>
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("banner.png", use_container_width=True)

st.markdown("1. Acesse seu marketplace ou ERP")
st.markdown("2. Baixe individualmente ou em lote o XML de suas vendas")
st.markdown("3. Importe seus arquivos para o Data Seller")

uploaded_files = st.file_uploader("Arquivos (.xml ou .zip)", type=["xml", "zip"], accept_multiple_files=True)

st.markdown(
    """
    <style>
    .processar-button {
        display: inline-block;
        background-color: black;
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        border-radius: 6px;
        text-align: center;
        text-decoration: none;
        font-weight: 500;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if uploaded_files:
    

    temp_dir = tempfile.TemporaryDirectory()
    path_dir = temp_dir.name
    dados = []
    canceladas = set()

    for uploaded in uploaded_files:
        file_path = os.path.join(path_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        if uploaded.name.lower().endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(path_dir)

    xml_files = []
    for root_dir, dirs, files in os.walk(path_dir):
        for file in files:
            if file.lower().endswith('.xml') or '-nfe.xml' in file.lower():
                xml_files.append(os.path.join(root_dir, file))

    nfe_files = [f for f in xml_files if '-110111' not in f]
    evento_files = [f for f in xml_files if 'procEventoNFe' in f]
    ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

    for evento_file in evento_files:
        try:
            tree = ET.parse(evento_file)
            root = tree.getroot()
            chave = root.find('.//ns:chNFe', ns)
            desc_evento = root.find('.//ns:descEvento', ns)
            if chave is not None and desc_evento is not None and 'Cancelamento' in desc_evento.text:
                canceladas.add(chave.text.strip())
        except:
            pass

    for nfe_file in nfe_files:
        try:
            tree = ET.parse(nfe_file)
            root = tree.getroot()
            infNFe = root.find('.//ns:infNFe', ns)
            if infNFe is None:
                infNFe = root.find('.//infNFe')
            if infNFe is None:
                continue

            chave = infNFe.attrib.get('Id', '')[3:] if 'Id' in infNFe.attrib else ''
            data_raw = root.findtext('.//ns:ide/ns:dhEmi', default='', namespaces=ns)
            data_venda = data_raw[:10] if data_raw else ''
            numero_venda = root.findtext('.//ns:ide/ns:nNF', default='', namespaces=ns)
            nome_cliente = root.findtext('.//ns:dest/ns:xNome', default='', namespaces=ns)
            telefone = root.findtext('.//ns:dest/ns:enderDest/ns:fone', default='', namespaces=ns)
            email = root.findtext('.//ns:dest/ns:email', default='', namespaces=ns)
            estado = root.findtext('.//ns:dest/ns:enderDest/ns:UF', default='', namespaces=ns)
            sku = root.findtext('.//ns:det/ns:prod/ns:cProd', default='', namespaces=ns)
            xped = root.findtext('.//ns:det/ns:prod/ns:xPed', default='', namespaces=ns)
            produto = root.findtext('.//ns:det/ns:prod/ns:xProd', default='', namespaces=ns)
            nf_cancelada = 'Sim' if chave in canceladas else 'Não'

            telefone_formatado = ''.join(filter(str.isdigit, telefone))
            link_whatsapp = f"https://wa.me/55{telefone_formatado}" if telefone_formatado else ''

            if len(telefone_formatado) >= 10:
                ddd = telefone_formatado[:2]
                numero = telefone_formatado[2:]
                telefone_formatado = f"+55({ddd}){numero}"

            dados.append({
                'Data da Venda': data_venda,
                'Nome': nome_cliente,
                'Telefone': telefone_formatado,
                'WhatsApp': link_whatsapp,
                'E-mail': email,
                'Estado': estado,
                'Número da Venda': numero_venda,
                'Número do Pedido': xped,
                'Produto': produto,
                'Observações': f"SKU: {sku} | Cancelada: {nf_cancelada}",
                'Notas Internas': ''
            })
        except Exception as e:
            st.warning(f"Erro lendo {nfe_file}: {e}")

    if dados:
        df = pd.DataFrame(dados)
        df['Data da Venda'] = pd.to_datetime(df['Data da Venda'], errors='coerce')
        df = df.sort_values(by='Data da Venda', ascending=False)

        st.success(f"✅ {len(df)} contatos processados com sucesso!")

        def make_clickable(link):
            return f'<a href="{link}" target="_blank">📞 Abrir</a>' if link else ''

        df['WhatsApp'] = df['WhatsApp'].apply(make_clickable)

        st.markdown("### Resultado")
        st.markdown("Clique no ícone do WhatsApp para iniciar uma conversa com o cliente.")

        # Criar um buffer para o Excel
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # Botão para download
        st.download_button(
        label="📥 Baixar Excel com os dados",
        data=excel_buffer,
        file_name="data_seller_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        with st.expander("🔍 Filtrar dados por coluna"):
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            col8, col9 = st.columns(2)
            filtros = {
                'Nome': col1.text_input("Filtrar Nome"),
                'Telefone': col2.text_input("Filtrar Telefone"),
                'E-mail': col8.text_input("Filtrar E-mail"),
                'Estado': col9.text_input("Filtrar Estado"),
                'Número da Venda': col3.text_input("Filtrar Nº Venda"),
                'Número do Pedido': col4.text_input("Filtrar Nº Pedido"),
                'Produto': col5.text_input("Filtrar Produto"),
                'Observações': col6.text_input("Filtrar Observações"),
                'Notas Internas': col7.text_input("Filtrar Notas Internas")
            }
            for coluna, valor in filtros.items():
                if valor:
                    df = df[df[coluna].astype(str).str.contains(valor, case=False, na=False)]

        st.markdown("""
    <style>
    .styled-table {
        font-size: 13px;
        border-collapse: collapse;
        width: 100%;
    }
    .styled-table th, .styled-table td {
        padding: 6px 10px;
        text-align: middle;
    }
    .styled-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)
        st.markdown(df.to_html(classes="styled-table", escape=False, index=False), unsafe_allow_html=True)
        
    else:
        st.warning("Nenhum contato foi encontrado.")

    with st.expander("🔒 Política de Privacidade"):
        st.markdown("""
        ## 🔒 Política de Privacidade

        O DATA SELLER respeita sua privacidade e está comprometido com a proteção dos dados pessoais processados na plataforma.

        ### 📥 Coleta de Dados

        Os dados utilizados no sistema são fornecidos diretamente pelo usuário, por meio do upload manual de arquivos XML de vendas (Notas Fiscais Eletrônicas). Não realizamos qualquer coleta automática ou em segundo plano.

        ### 🧠 Finalidade

        O objetivo do sistema é exclusivamente facilitar o acesso aos dados de venda para fins legítimos de:

        - Organização de contatos comerciais;
        - Comunicação com compradores (ex: envio de mensagens relacionadas à compra);
        - Gestão interna de vendas e histórico.

        Não utilizamos os dados para envio de publicidade não solicitada.

        ### 🛑 Compartilhamento

        Nenhum dado é compartilhado com terceiros, parceiros, agências ou plataformas externas. O uso é 100% local e sob controle do próprio usuário.

        ### ⏳ Armazenamento

        Os dados processados não são salvos em servidores. O processamento ocorre localmente e temporariamente durante o uso do sistema.

        ### 🔐 Segurança

        Se o sistema estiver acessível via internet, medidas de segurança como login, autenticação e controle de acesso são aplicadas para proteger os dados contra acessos não autorizados.

        ### 📄 Base Legal

        O tratamento dos dados segue as bases legais previstas na LGPD, especialmente:

        - **Execução de contrato** (venda já realizada);
        - **Legítimo interesse** do fornecedor em contatar o cliente para suporte, confirmação ou relacionamento;
        - **Consentimento**, caso necessário para comunicações adicionais.

        ### 📞 Dúvidas

        Em caso de dúvidas, entre em contato com o responsável pela operação do sistema.
        """)
