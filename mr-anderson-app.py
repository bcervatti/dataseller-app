# Para rodar este app, use o terminal com:
# streamlit run mr-anderson-app.py

import os
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st # type: ignore
import tempfile
import zipfile
from datetime import datetime

st.set_page_config(page_title="DATA SELLER v1.1 | Amplie suas vendas e fortaleça sua comunidade", layout="wide")
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
st.image("logo.png", width=180)
##st.title("📊 DATA SELLER v1.1")
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
    processar = st.markdown(
        f"""
        <form action="#" method="post">
            <button class="processar-button" type="submit">Processar</button>
        </form>
        """,
        unsafe_allow_html=True
    )

    # Botão alternativo invisível que ativa o processamento real
    if st.button("Clique aqui para Processar (invisível)"):
        st.session_state.run_processing = True

    if st.session_state.get("run_processing"):
        st.session_state.run_processing = False
        # (resto do processamento segue aqui normalmente...)
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
                infNFe = root.find('.//infNFe')  # fallback sem namespace
            if infNFe is None:
                continue

            chave = infNFe.attrib.get('Id', '')[3:] if 'Id' in infNFe.attrib else ''
            data_raw = root.findtext('.//ns:ide/ns:dhEmi', default='', namespaces=ns)
            data_venda = data_raw[:10] if data_raw else ''
            numero_venda = root.findtext('.//ns:ide/ns:nNF', default='', namespaces=ns)
            nome_cliente = root.findtext('.//ns:dest/ns:xNome', default='', namespaces=ns)
            telefone = root.findtext('.//ns:dest/ns:enderDest/ns:fone', default='', namespaces=ns)
            sku = root.findtext('.//ns:det/ns:prod/ns:cProd', default='', namespaces=ns)
            xped = root.findtext('.//ns:det/ns:prod/ns:xPed', default='', namespaces=ns)
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
                'Número da Venda': numero_venda,
                'Número do Pedido': xped,
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
            return f'<a href="{link}" target="_blank">📲 Abrir</a>' if link else ''

        df['WhatsApp'] = df['WhatsApp'].apply(make_clickable)

        st.markdown("### Resultado")
        st.markdown("Clique no ícone do WhatsApp para iniciar uma conversa com o cliente.")
        st.markdown("Campo 'Notas Internas' está disponível para observações manuais.")
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("Nenhum contato foi encontrado.")