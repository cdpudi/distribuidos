import streamlit as st
import requests
import json
import os

DB_FILE = "database.json"

# ---------- FUNÇÕES ----------

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(DB_FILE, "w") as f:
        json.dump(dados, f, indent=2)

# ---------- UI ----------

st.set_page_config(page_title="Validação Sistemas Distribuídos", layout="wide")

st.title("🚀 Sistema de Validação de Atividades")

menu = st.sidebar.radio("Menu", ["Cadastrar Grupo", "Grupos"])

dados = carregar_dados()

# ---------- CADASTRO ----------

if menu == "Cadastrar Grupo":
    st.header("📋 Cadastro do Grupo")

    grupo = st.text_input("Nome do Grupo")
    alunos = st.text_area("Alunos (um por linha)")
    webhook = st.text_input("Webhook")

    if st.button("Salvar Grupo"):
        novo = {
            "grupo": grupo,
            "alunos": alunos.split("\n"),
            "webhook": webhook,
            "status": "PENDENTE"
        }

        dados.append(novo)
        salvar_dados(dados)

        st.success("Grupo cadastrado com sucesso!")

# ---------- LISTAGEM ----------

if menu == "Grupos":
    st.header("📊 Grupos Cadastrados")

    if len(dados) == 0:
        st.warning("Nenhum grupo cadastrado.")
    else:
        for i, g in enumerate(dados):
            with st.container():
                st.markdown("---")

                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.subheader(g["grupo"])
                    st.write("👥 Alunos:")
                    for aluno in g["alunos"]:
                        st.write(f"- {aluno}")

                with col2:
                    if g["status"] == "APROVADO":
                        st.success("✅ APROVADO")
                    else:
                        st.warning("⏳ PENDENTE")

                with col3:
                    if st.button("Validar", key=i):
                        try:
                            r = requests.post(g["webhook"], json=g)

                            if r.status_code == 200:
                                dados[i]["status"] = "APROVADO"
                                salvar_dados(dados)
                                st.success("Validado!")
                            else:
                                st.error("Erro na validação")

                        except:
                            st.error("Webhook não respondeu")
