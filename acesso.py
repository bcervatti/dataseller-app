import streamlit as st
from PIL import Image

st.set_page_config(page_title="DATA SELLER | Assinatura", layout="centered")

# Estilos globais
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
            background-color: #ffffff;
        }
        img {
            border-radius: 1px;
            margin-bottom: 1px;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# 🖼️ Imagem de capa
imagem_capa = Image.open("acesso_capa.png")
st.image(imagem_capa, use_container_width=True)

st.divider()

# 🔴 Assinatura
st.markdown("#### Assine por apenas **R$ 19,90/mês**")
st.markdown("e comece hoje mesmo a fidelizar seus clientes")

link_assinatura = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=2c93808496eba93f0196ef4d59bc01a4"

st.markdown(
    f"""
    <a href="{link_assinatura}" target="_blank" style='
        display: inline-block;
        background-color: red;
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        border-radius: 6px;
        text-align: center;
        text-decoration: none;
        width: 100%;
        font-weight: 500;
        margin-top: 1rem;
    '>
    ASSINE AGORA
    </a>
    """,
    unsafe_allow_html=True
)

st.caption("Após o pagamento, seu acesso será liberado automaticamente ou em até 5 minutos.")
