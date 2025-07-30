from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

# Deleta todos os vetores
vectorstore._index.delete(delete_all=True)

print(f"Todos os vetores do índice '{index_name}' foram removidos com sucesso.")
