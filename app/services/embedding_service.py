import openai
import os
from dotenv import load_dotenv
from pathlib import Path

# Garante que o .env da raiz seja carregado corretamente
load_dotenv(dotenv_path=Path('.') / '.env')

# Inicializa o cliente com a chave da API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_embedding(texto: str) -> list:
    response = client.embeddings.create(
        input=texto,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
