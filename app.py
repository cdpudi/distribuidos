import streamlit as st
import requests
import json
import os
from datetime import datetime

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

st.set_page_config(page_title="Validação Sistemas Distribuídos", layout="wide")
st.title("🚀 Sistema de Validação - Sistemas Distribuídos")

menu = st.sidebar.radio("Menu", ["Cadastrar Grupo", "Grupos"])

data = load_data()

# ---------------- CADASTRO ----------------

if menu == "Cadastrar Grupo":
    st.header("📋 Cadastro do Grupo")

    grupo = st.text_input("Nome do Grupo")
    alunos = st.text_area("Alunos (um por linha)")
    webhook = st.text_input("Webhook de Teste")

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

        st.success("Grupo cadastrado com sucesso!")

# ---------------- LISTAGEM ----------------

if menu == "Grupos":
    st.header("📊 Grupos Cadastrados")

    if len(data) == 0:
        st.warning("Nenhum grupo cadastrado.")
    else:
        for i, g in enumerate(data):
            st.markdown("---")

            col1, col2 = st.columns([3,1])

            with col1:
                st.subheader(g["grupo"])
                st.write("👥 Alunos:")
                for aluno in g["alunos"]:
                    if aluno.strip():
                        st.write(f"- {aluno}")

                st.write("🌐 Infraestrutura:")
                st.json(g["infra"])

            with col2:
                if g["status"] == "ENVIADO":
                    st.info("📤 ENVIADO")
                else:
                    st.warning("⏳ PENDENTE")

            colA, colB, colC = st.columns(3)

            # -------- ENVIAR --------
            with colA:
                if g["status"] == "PENDENTE":
                    if st.button("📤 Enviar Grupo", key=f"send{i}"):
                        try:
                            payload = {
                                "grupo": g["grupo"],
                                "alunos": g["alunos"],
                                "infra": g["infra"],
                                "data_envio": str(datetime.now())
                            }

                            r = requests.post(
                                WEBHOOK_ENVIO,
                                json=payload,
                                timeout=10
                            )

                            st.write("Status HTTP:", r.status_code)

                            try:
                                st.json(r.json())
                            except:
                                st.text(r.text)

                            if r.status_code == 200:
                                data[i]["status"] = "ENVIADO"
                                save_data(data)
                                st.success("Grupo enviado com sucesso!")
                            else:
                                st.error("Erro ao enviar webhook")

                        except Exception as e:
                            st.error(f"Erro real: {str(e)}")
                else:
                    st.button("🔒 Enviado", disabled=True, key=f"lock{i}")

            # -------- TESTAR WEBHOOK --------
            with colB:
                if st.button("🧪 Testar", key=f"test{i}"):
                    try:
                        r = requests.post(g["webhook"], timeout=10)

                        st.write("Status HTTP:", r.status_code)

                        try:
                            resp = r.json()
                            st.json(resp)
                        except:
                            st.text(r.text)

                    except Exception as e:
                        st.error(f"Erro: {str(e)}")

            # -------- EXCLUIR --------
            with colC:
                if st.button("🗑️ Excluir", key=f"del{i}"):
                    data.pop(i)
                    save_data(data)
                    st.success("Grupo removido!")
                    st.rerun()
