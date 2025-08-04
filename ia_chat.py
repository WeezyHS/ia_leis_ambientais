import streamlit as st
import requests
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="IA - Leis Ambientais", layout="wide")
st.title("🤖 IA - Consulta de Leis Ambientais do Tocantins")

# Inicialização do estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "leis_relacionadas" not in st.session_state:
    st.session_state.leis_relacionadas = []

# Função para extrair número da lei do título
def extrair_numero_lei(titulo):
    match = re.search(r"LEI N[º°\.]?\s*(\d{1,2}\.\d{3}|\d{4,5})", titulo.upper())
    if match:
        numero = match.group(1)
        if '.' not in numero and len(numero) == 4:
            return f"{numero[0]}.{numero[1:]}"
        elif '.' not in numero and len(numero) == 5:
            return f"{numero[:2]}.{numero[2:]}"
        return numero
    return None

# Interface de chat
with st.container():
    # Entrada do usuário
    pergunta = st.chat_input("Digite sua pergunta sobre leis ambientais...")

    if pergunta:
        st.session_state.chat_history.append(("usuário", pergunta))

        with st.spinner("Consultando base de leis ambientais..."):
            try:
                resposta = requests.post("http://localhost:8000/consulta", json={"pergunta": pergunta})
                resposta.raise_for_status()
                dados = resposta.json()
                resposta_ia = dados.get("resposta", "Não foi possível gerar uma resposta.")
                st.session_state.leis_relacionadas = dados.get("leis_relacionadas", [])
            except Exception as e:
                st.error(f"❌ Erro na requisição: {e}")
                st.stop()

            st.session_state.chat_history.append(("ia", resposta_ia))

    # Exibe o histórico de mensagens
    for autor, texto in st.session_state.chat_history:
        with st.chat_message(autor):
            st.markdown(texto)