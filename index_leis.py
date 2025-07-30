import hashlib
import json
from app.services.embedding_service import gerar_embedding
from app.services.pinecone_service import indexar_no_pinecone

with open("tests/leis.json", "r", encoding="utf-8") as f:
    leis = json.load(f)

itens_para_indexar = []

for lei in leis:
    titulo = lei["titulo"]
    descricao = lei["descricao"]
    conteudo = lei["conteudo"]

    # ✅ Geração do ID único com base em título + descrição
    base_id = (titulo + descricao).strip().lower()
    id_lei = hashlib.md5(base_id.encode("utf-8")).hexdigest()

    texto_completo = f"{titulo}\n{descricao}\n{conteudo}"
    embedding = gerar_embedding(texto_completo)

    itens_para_indexar.append({
        "id": id_lei,
        "values": embedding,
        "metadata": {
            "titulo": titulo,
            "descricao": descricao,
            "conteudo": conteudo
        }
    })

indexar_no_pinecone(itens_para_indexar)
