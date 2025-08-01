import os
import re
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from app.services.pinecone_service import vectorstore

def extrair_numero_lei(pergunta: str):
    # Captura formatos com ou sem ponto
    match = re.search(r"lei(?: nº| número)?\s*(\d{4,5}|\d{1,2}\.\d{3})", pergunta.lower())
    if match:
        numero = match.group(1)
        if '.' in numero:
            return numero  # Já está no formato correto
        # Corrige número sem ponto
        if len(numero) == 4:
            return f"{numero[0]}.{numero[1:]}"     # 3519 → 3.519
        elif len(numero) == 5:
            return f"{numero[:2]}.{numero[2:]}"    # 12345 → 12.345
    return None

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

def consultar_lei(pergunta: str) -> dict:
    numero_lei = extrair_numero_lei(pergunta)

    # 🔍 Busca por número específico
    if numero_lei:
        documentos = vectorstore.similarity_search(
            query=f"lei {numero_lei}",
            k=5,
            filter={
                "$or": [
                    {"numero_lei": numero_lei},
                    {"numero_lei_puro": numero_lei.replace(".", "")}
                ]
            }
        )

        if documentos:
            resposta = f"As informações da Lei {numero_lei} são:\n\n" + "\n\n".join(
                [doc.page_content for doc in documentos]
            )
            leis_relacionadas = [
                {
                    "titulo": doc.metadata.get("titulo", "Sem título"),
                    "descricao": doc.metadata.get("descricao", ""),
                    "conteudo": doc.page_content
                }
                for doc in documentos
            ]
            return {
                "resposta": resposta,
                "leis_relacionadas": leis_relacionadas
            }

    # 🤖 Caso não tenha número ou não encontrou diretamente
    resultado = qa_chain(pergunta)
    resposta = resultado["result"]
    documentos = resultado.get("source_documents", [])

    leis_relacionadas = [
        {
            "titulo": doc.metadata.get("titulo", "Sem título"),
            "descricao": doc.metadata.get("descricao", ""),
            "conteudo": doc.page_content
        }
        for doc in documentos
    ]

    return {
        "resposta": resposta,
        "leis_relacionadas": leis_relacionadas
    }
