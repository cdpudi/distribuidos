import streamlit as st
import requests
import json
import os

DB_FILE = "database.json"
WEBHOOK_ENVIO = "https://alunos.umg.com.br/webhook/recebe_distribuido"

# ---------------- FUNÇÕES ----------------

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- CONFIG ----------------

st.set_page_config(layout="wide")
st.title("🚀 Sistema de Validação - Sistemas Distribuídos")

menu = st.sidebar.radio("Menu", ["Cadastrar Grupo", "Grupos"])

data = load_data()

# ---------------- CADASTRO ----------------

if menu == "Cadastrar Grupo":
    st.header("📋 Cadastro do Grupo")

    grupo = st.text_input("Nome do Grupo")
    alunos = st.text_area("Alunos (um por linha)")
    webhook = st.text_input("Webhook de Validação")

    st.subheader("🌐 Infraestrutura")

    aws = st.text_input("AWS (Link)")
    ip = st.text_input("IP")
    ddns = st.text_input("DDNS")
    easypanel = st.text_input("EasyPanel")
    n8n = st.text_input("n8n")
    pgadmin = st.text_input("pgAdmin")

    if st.button("Salvar Grupo"):
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

        st.success("Grupo cadastrado!")

# ---------------- LISTAGEM ----------------

if menu == "Grupos":
    st.header("📊 Grupos")

    for i, g in enumerate(data):
        st.markdown("---")

        col1, col2 = st.columns([3,1])

        with col1:
            st.subheader(g["grupo"])
            st.write("👥 Alunos:", ", ".join(g["alunos"]))
            st.json(g["infra"])

        with col2:
            if g["status"] == "APROVADO":
                st.success("APROVADO")
            elif g["status"] == "ENVIADO":
                st.info("ENVIADO")
            else:
                st.warning("PENDENTE")

        colA, colB, colC, colD = st.columns(4)

        # -------- ENVIAR --------
        with colA:
            if g["status"] == "PENDENTE":
                if st.button("📤 Enviar Grupo", key=f"send{i}"):
                    try:
                        payload = g
                        r = requests.post(WEBHOOK_ENVIO, json=payload)

                        if r.status_code == 200:
                            data[i]["status"] = "ENVIADO"
                            save_data(data)
                            st.success("Grupo enviado com sucesso!")
                        else:
                            st.error("Erro ao enviar")

                    except Exception as e:
                        st.error(str(e))
            else:
                st.button("🔒 Enviado", disabled=True, key=f"lock{i}")

        # -------- TESTAR --------
        with colB:
            if st.button("🧪 Testar", key=f"test{i}"):
                try:
                    r = requests.post(g["webhook"])

                    if r.status_code == 200:
                        st.json(r.json())
                    else:
                        st.error("Erro HTTP")
                except:
                    st.error("Erro webhook")

        # -------- VALIDAR --------
        with colC:
            if st.button("✅ Validar", key=f"val{i}"):
                try:
                    r = requests.post(g["webhook"])

                    if r.status_code == 200:
                        resp = r.json()

                        if (
                            isinstance(resp, list)
                            and len(resp) > 0
                            and resp[0].get("acao") == "teste inicial"
                        ):
                            data[i]["status"] = "APROVADO"
                            save_data(data)
                            st.success("Validado!")
                        else:
                            st.error("JSON inválido")
                    else:
                        st.error("Erro HTTP")
                except:
                    st.error("Erro webhook")

        # -------- EDITAR --------
        with colD:
            if g["status"] == "PENDENTE":
                if st.button("✏️ Editar", key=f"edit{i}"):
                    st.session_state["edit_index"] = i
            else:
                st.button("🔒 Bloqueado", disabled=True, key=f"blocked{i}")

    # -------- FORM EDIT --------
    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]
        g = data[idx]

        st.markdown("---")
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
