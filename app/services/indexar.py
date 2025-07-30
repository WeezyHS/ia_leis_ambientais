from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
import os
import hashlib

from dotenv import load_dotenv
load_dotenv()

index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

def gerar_id_unico(texto: str) -> str:
    """Gera um hash MD5 a partir do texto para usar como ID único."""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()

def indexar_leis(leis: list[dict]):
    """
    Indexa uma lista de leis no Pinecone, evitando duplicações.
    Cada item deve ter: {"titulo": ..., "descricao": ...}
    """
    documentos = []
    ids = []

    for lei in leis:
        conteudo = f"{lei['titulo']}\n\n{lei['descricao']}"
        doc_id = gerar_id_unico(conteudo)
        doc = Document(page_content=conteudo, metadata={"titulo": lei["titulo"]})
        documentos.append(doc)
        ids.append(doc_id)

    vectorstore.add_documents(documentos, ids=ids)
    return len(documentos)
