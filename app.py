import streamlit as st
import requests

st.title("Validação de Webhook")

webhook = st.text_input("Webhook")

if st.button("Testar"):
    try:
        r = requests.post(webhook)

        if r.status_code == 200:
            st.success("OK")
        else:
            st.error("Erro")
    except:
        st.error("Falha conexão")
