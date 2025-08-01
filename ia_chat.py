import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="IA - Leis Ambientais", layout="wide")
st.title("🤖 IA - Consulta de Leis Ambientais")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

pergunta = st.chat_input("Digite sua pergunta sobre leis...")

if pergunta:
    st.session_state.chat_history.append(("usuário", pergunta))

    with st.spinner("Consultando IA..."):
        try:
            resposta = requests.post("http://localhost:8000/consulta", json={"pergunta": pergunta})
            resposta.raise_for_status()
            dados = resposta.json()
            resposta_ia = dados.get("resposta", "Não foi possível gerar uma resposta.")
        except Exception as e:
            st.error(f"❌ Erro na requisição: {e}")
            st.stop()

        st.session_state.chat_history.append(("ia", resposta_ia))

# 💬 Exibe o histórico de mensagens
for autor, texto in st.session_state.chat_history:
    with st.chat_message(autor):
        st.markdown(texto)

# 📊 Geração da planilha vazia
colunas = ["Número da Lei", "Título", "Descrição", "Conteúdo resumido", "Observações"]
df = pd.DataFrame(columns=colunas)

st.subheader("📋 Prévia da planilha gerada")
st.dataframe(df, use_container_width=True)

buffer = BytesIO()
df.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)

st.download_button(
    label="📥 Baixar planilha Excel",
    data=buffer,
    file_name="resultado_ia.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
