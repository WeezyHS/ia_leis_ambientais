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
