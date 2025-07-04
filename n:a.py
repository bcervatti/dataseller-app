import streamlit as st
import pandas as pd
from lxml import etree
import base64

st.set_page_config(page_title="DATA SELLER v1.2", layout="wide")
st.title("📦 DATA SELLER v1.2")

st.markdown("Faça upload de arquivos XML da NFe para visualizar os dados.")

uploaded_files = st.file_uploader("Upload de arquivos XML", type=["xml"], accept_multiple_files=True)

@st.cache_data
def parse_xml(file):
    tree = etree.parse(file)
    root = tree.getroot()

    records = []
    ide_nNF = root.find(".//{*}nNF")
    numero_nf = ide_nNF.text if ide_nNF is not None else ""

    for det in root.findall(".//{*}det"):
        nItem = det.attrib.get("nItem", "")
        prod = det.find(".//{*}prod")
        if prod is not None:
            cProd = prod.findtext(".//{*}cProd", default="")
            xProd = prod.findtext(".//{*}xProd", default="")
            # Simulação de dados extras:
            nome = "Cliente Exemplo"
            telefone = "(11) 99999-9999"
            num_venda = "123456"
            num_pedido = "654321"
            obs = "Sem observações"
            records.append({
                "Nome": nome,
                "Telefone": telefone,
                "Nº Venda": num_venda,
                "Nº Pedido": num_pedido,
                "Observações": obs,
                "Produto": xProd
            })
    return records

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        parsed = parse_xml(file)
        all_data.extend(parsed)

    df = pd.DataFrame(all_data)

    # Interface de filtros por coluna
    st.subheader("🔎 Filtros por Coluna")

    filters = {}
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    filters["Nome"] = col1.text_input("Filtrar Nome")
    filters["Telefone"] = col2.text_input("Filtrar Telefone")
    filters["Nº Venda"] = col3.text_input("Filtrar Nº Venda")
    filters["Nº Pedido"] = col4.text_input("Filtrar Nº Pedido")
    filters["Observações"] = col5.text_input("Filtrar Observações")
    filters["Produto"] = col6.text_input("Filtrar Produto")

    for key, value in filters.items():
        if value:
            df = df[df[key].str.contains(value, case=False, na=False)]

    st.dataframe(df, use_container_width=True)