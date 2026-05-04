import streamlit as st
import requests
import json
import os

DB_FILE = "database.json"

def salvar_dados(dados):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    else:
        db = []

    db.append(dados)

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


st.title("Sistema de Validação - Sistemas Distribuídos")

# Cadastro
st.header("Cadastro do Grupo")

grupo = st.text_input("Nome do Grupo")
alunos = st.text_area("Alunos (um por linha)")
ip = st.text_input("IP da VPS")
webhook = st.text_input("Webhook")

if st.button("Salvar"):
    dados = {
        "grupo": grupo,
        "alunos": alunos.split("\n"),
        "ip": ip,
        "webhook": webhook,
        "status": "PENDENTE"
    }
    salvar_dados(dados)
    st.success("Grupo cadastrado!")

# Validação
st.header("Validar Grupo")

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        db = json.load(f)

    for item in db:
        st.subheader(item["grupo"])
        st.write("Status:", item["status"])

        if st.button(f"Validar {item['grupo']}"):
            try:
                r = requests.post(item["webhook"], json=item)

                if r.status_code == 200:
                    item["status"] = "APROVADO"
                    st.success("Validado com sucesso!")
                else:
                    st.error("Erro na validação")

            except:
                st.error("Webhook não respondeu")

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)
