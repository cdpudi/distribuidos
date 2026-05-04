import streamlit as st
import requests
import json
import os

DB_FILE = "database.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

st.set_page_config(layout="wide")
st.title("🚀 Sistema de Validação - Sistemas Distribuídos")

menu = st.sidebar.radio("Menu", ["Cadastrar", "Grupos"])

data = load_data()

# ---------------- CADASTRO ----------------
if menu == "Cadastrar":
    st.header("📋 Cadastro do Grupo")

    grupo = st.text_input("Nome do Grupo")
    alunos = st.text_area("Alunos (um por linha)")
    webhook = st.text_input("Webhook")

    st.subheader("🌐 Infraestrutura")

    aws = st.text_input("AWS Link")
    ip = st.text_input("IP")
    ddns = st.text_input("DDNS")

    easypanel = st.text_input("EasyPanel URL")
    n8n = st.text_input("n8n URL")
    pgadmin = st.text_input("pgAdmin URL")

    if st.button("Salvar"):
        novo = {
            "grupo": grupo,
            "alunos": alunos.split("\n"),
            "webhook": webhook,
            "infra": {
                "aws": aws,
                "ip": ip,
                "ddns": ddns,
                "easypanel": easypanel,
                "n8n": n8n,
                "pgadmin": pgadmin
            },
            "status": "PENDENTE"
        }

        data.append(novo)
        save_data(data)
        st.success("Grupo salvo!")

# ---------------- LISTAGEM ----------------
if menu == "Grupos":
    st.header("📊 Grupos")

    for i, g in enumerate(data):
        st.markdown("---")

        col1, col2 = st.columns([3,1])

        with col1:
            st.subheader(g["grupo"])
            st.write("👥 Alunos:", ", ".join(g["alunos"]))

            st.write("🌐 Infraestrutura:")
            st.write(g["infra"])

        with col2:
            if g["status"] == "APROVADO":
                st.success("APROVADO")
            else:
                st.warning("PENDENTE")

        colA, colB = st.columns(2)

        # -------- VALIDAR --------
        with colA:
            if st.button("Validar", key=f"v{i}"):
                try:
                    r = requests.post(g["webhook"])

                    if r.status_code == 200:
                        resp = r.json()

                        # valida formato
                        if isinstance(resp, list) and "acao" in resp[0]:
                            data[i]["status"] = "APROVADO"
                            save_data(data)
                            st.success("Validação OK")
                        else:
                            st.error("Formato inválido")

                    else:
                        st.error("Erro HTTP")

                except:
                    st.error("Erro webhook")

        # -------- EDITAR --------
        with colB:
            if st.button("Editar", key=f"e{i}"):
                st.session_state["edit_index"] = i

    # -------- FORM EDIT --------
    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]
        g = data[idx]

        st.header("✏️ Editar Grupo")

        grupo = st.text_input("Nome", g["grupo"])
        alunos = st.text_area("Alunos", "\n".join(g["alunos"]))
        webhook = st.text_input("Webhook", g["webhook"])

        aws = st.text_input("AWS", g["infra"]["aws"])
        ip = st.text_input("IP", g["infra"]["ip"])
        ddns = st.text_input("DDNS", g["infra"]["ddns"])
        easypanel = st.text_input("EasyPanel", g["infra"]["easypanel"])
        n8n = st.text_input("n8n", g["infra"]["n8n"])
        pgadmin = st.text_input("pgAdmin", g["infra"]["pgadmin"])

        if st.button("Atualizar"):
            data[idx] = {
                "grupo": grupo,
                "alunos": alunos.split("\n"),
                "webhook": webhook,
                "infra": {
                    "aws": aws,
                    "ip": ip,
                    "ddns": ddns,
                    "easypanel": easypanel,
                    "n8n": n8n,
                    "pgadmin": pgadmin
                },
                "status": g["status"]
            }

            save_data(data)
            del st.session_state["edit_index"]
            st.success("Atualizado!")
