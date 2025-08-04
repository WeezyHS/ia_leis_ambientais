from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os

index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

def search_similar_documents(texto: str, top_k: int = 5):
    docs = vectorstore.similarity_search(texto, k=top_k)
    return [{"texto": d.page_content, "metadado": d.metadata} for d in docs]

def indexar_no_pinecone(itens):
    """
    itens: lista de dicionários no formato:
    {
        "id": "abc123",
        "values": [...],
        "metadata": {
            "titulo": "...",
            "descricao": "...",
            "conteudo": "..."
        }
    }
    """
    # LangChain espera documentos, então criamos os objetos apropriados
    from langchain_core.documents import Document

    documentos = [
        Document(
            page_content=item["metadata"]["conteudo"],
            metadata={
                "id": item["id"],
                "titulo": item["metadata"]["titulo"],
                "descricao": item["metadata"]["descricao"],
                "numero_lei": item["metadata"].get("numero_lei"),
                "numero_lei_puro": item["metadata"].get("numero_lei_puro")
            }
        )
        for item in itens
    ]

    vectorstore.add_documents(documentos)
    print(f"{len(documentos)} documentos enviados ao Pinecone com sucesso.")
