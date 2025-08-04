from typing import List
from langchain_core.documents import Document
from app.services.pinecone_service import vectorstore
from app.services.text_normalizer import normalizar_pergunta_busca

def buscar_documentos_com_normalizacao(query: str, k: int = 4) -> List[Document]:
    """
    Busca documentos relevantes aplicando normalização de texto.
    Otimizada para evitar buscas desnecessárias e reduzir uso de memória.
    """
    # Normaliza a query
    query_normalizada = normalizar_pergunta_busca(query)
    
    # Se a query normalizada é muito similar à original, faz apenas uma busca
    if query_normalizada.lower().strip() == query.lower().strip():
        return vectorstore.similarity_search(query=query, k=k)
    
    # Caso contrário, prioriza a busca normalizada (mais eficaz para acentos)
    docs_normalizada = vectorstore.similarity_search(query=query_normalizada, k=k)
    
    # Se não encontrou resultados suficientes, complementa com busca original
    if len(docs_normalizada) < k:
        docs_original = vectorstore.similarity_search(query=query, k=k-len(docs_normalizada))
        
        # Remove duplicatas simples baseado no conteúdo
        conteudos_existentes = {doc.page_content[:100] for doc in docs_normalizada}
        docs_original_filtrados = [
            doc for doc in docs_original 
            if doc.page_content[:100] not in conteudos_existentes
        ]
        
        docs_normalizada.extend(docs_original_filtrados)
    
    return docs_normalizada[:k]