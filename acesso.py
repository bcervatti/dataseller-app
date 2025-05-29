import streamlit as st
import sqlite3
import re
import bcrypt
import requests
import urllib.parse

st.set_page_config(page_title="DATA SELLER | Acesso", layout="centered")

# Fonte e estilo Roboto + ajustes visuais
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        background-color: #ffffff;
    }
    .login-button {
        padding: 0.6rem 1.2rem;
        border: none;
        width: 100%;
        font-size: 1rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        background-color: #f2f2f2;
        color: #333;
        cursor: pointer;
        transition: 0.2s;
    }
    .login-button:hover {
        background-color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Logo e boas-vindas
col1, col2 = st.columns([1, 1.5])

with col1:
    st.image("logo.png", width=140)
    st.markdown("## Bem-vindo(a) novamente")
    st.markdown("Vamos te ajudar a se conectar")

# Verifica se há access_token no retorno da URL
params = st.query_params

if "access_token" in params:
    access_token = params["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers).json()

    email_google = user_info.get("email")

    if email_google:
        conn = sqlite3.connect("usuarios.db")
        c = conn.cursor()

        # Verifica se já existe esse email no banco
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email_google,))
        existe = c.fetchone()

        # Se não existir, insere com assinatura inativa
        if not existe:
            c.execute("INSERT INTO usuarios (email, documento, senha_hash, assinatura_ativa) VALUES (?, ?, ?, 0)", (email_google, "", "", 0))
            conn.commit()

        conn.close()
        st.success("✅ Acesso liberado via Google!")
        st.markdown("[Ir para o DATA SELLER](https://dataseller.streamlit.app/mr-anderson-app)")

with col2:
    st.markdown("### Entrar")

    # Login com Google
    client_id = "197511749083-09dujn1dvd2ebdd76dmtv8p9e525okgg.apps.googleusercontent.com"
    redirect_uri = "https://dataseller.streamlit.app"
    scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?response_type=token"
        f"&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&scope={urllib.parse.quote(scope)}&prompt=select_account"
    )
    ##st.markdown(f"<a href='{oauth_url}' class='login-button'> Acesso conta Google </a>", unsafe_allow_html=True)
    st.markdown(
    f"""
    <a href='{oauth_url}' target='_self' style='
        display: inline-block;
        background-color: black;
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        border-radius: 6px;
        text-align: center;
        text-decoration: none;
        width: 100%;
        font-weight: 500;
        margin: 0.3rem 0;
    '>
    Acesso com Google
    </a>
    """,
    unsafe_allow_html=True
)

    
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("#### Crie sua conta")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        documento = st.text_input("CPF ou CNPJ")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        conn = sqlite3.connect("usuarios.db")
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        resultado = c.fetchone()
        if resultado:
            senha_hash = resultado[2]
            if isinstance(senha_hash, str) and senha_hash.strip():
                if bcrypt.checkpw(senha.encode(), senha_hash.encode()):
                    if resultado[3]:
                        st.success("✅ Acesso liberado!")
                        st.markdown("[Ir para o DATA SELLER](https://dataselller.streamlit.app/)")
                    else:
                        st.warning("🔒 Assinatura inativa. Faça sua assinatura abaixo.")
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("⚠️ Esta conta foi criada via Google. Use o login com Google para entrar.")
        else:
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            c.execute("INSERT INTO usuarios (email, documento, senha_hash, assinatura_ativa) VALUES (?, ?, ?, 0)", (email, documento, senha_hash))
            conn.commit()
            st.info("Cadastro realizado! Agora ative sua assinatura para acessar.")

st.divider()

# Assinatura
st.markdown("#### Assine por apenas **R$ 9,99/mês**")
st.markdown("e comece hoje mesmo a fidelizar seus clientes")
link_assinatura = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=2c93808496eba93f0196ef4d59bc01a4"
##st.markdown(f"[🚀 Assinar Agora]({link_assinatura})")
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
