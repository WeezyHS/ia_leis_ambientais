import hashlib
import json
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import gerar_embedding
from app.services.pinecone_service import indexar_no_pinecone

# Função auxiliar para extrair o número da lei do título
def extrair_numero_lei(pergunta: str):
    match = re.search(r"lei(?: nº| número)?\s*([\d\.]{3,7})", pergunta.lower())
    if match:
        numero = match.group(1).replace(".", "")  # Remove ponto se tiver
        if len(numero) == 4:
            return f"{numero[0]}.{numero[1:]}"  # 3519 → 3.519
        elif len(numero) == 5:
            return f"{numero[:2]}.{numero[2:]}"  # 12345 → 12.345
    return None

# Teste da função de extração de número de lei
print("Teste de extração de número:")
print(extrair_numero_lei("LEI Nº 3.519 DE 5 DE AGOSTO DE 2019"))  # Esperado: 3.519
print(extrair_numero_lei("LEI Nº 12345 DE 1º DE JANEIRO DE 2020"))  # Esperado: 12.345

# Carregar as leis
with open("tests/leis.json", "r", encoding="utf-8") as f:
    leis = json.load(f)

itens_para_indexar = []

for lei in leis:
    titulo = lei["titulo"]
    descricao = lei["descricao"]
    conteudo = lei["conteudo"]

    base_id = (titulo + descricao).strip().lower()
    id_lei = hashlib.md5(base_id.encode("utf-8")).hexdigest()

    texto_completo = f"{titulo}\n{descricao}\n{conteudo}"
    embedding = gerar_embedding(texto_completo)

    numero = extrair_numero_lei(titulo)
    numero_sem_ponto = numero.replace(".", "") if numero else None

    itens_para_indexar.append({
        "id": id_lei,
        "values": embedding,
        "metadata": {
            "titulo": titulo,
            "descricao": descricao,
            "conteudo": conteudo,
            "numero_lei": numero,
            "numero_lei_puro": numero_sem_ponto
        }
    })

# Indexar no Pinecone
indexar_no_pinecone(itens_para_indexar)
