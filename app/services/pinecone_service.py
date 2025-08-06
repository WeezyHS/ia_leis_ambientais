from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os

index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

# Conexão direta com Pinecone para busca com namespace
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index(index_name)

def search_similar_documents(texto: str, top_k: int = 5):
    """Busca documentos similares incluindo normas ABNT"""
    
    # Gera embedding da consulta
    query_embedding = embeddings.embed_query(texto)
    
    # Busca em diferentes namespaces
    abnt_results = []
    leis_results = []
    coema_results = []
    
    try:
        # Busca no namespace ABNT
        abnt_response = pinecone_index.query(
            vector=query_embedding,
            top_k=3,
            namespace="abnt-normas",
            include_metadata=True
        )
        
        for match in abnt_response.matches:
             if match.score > 0.3:  # Filtro de relevância mais permissivo
                 # Para ABNT, o texto está no campo 'text' dos metadados
                 texto_abnt = match.metadata.get('text', match.metadata.get('content', match.metadata.get('conteudo', '')))
                 abnt_results.append({
                     "texto": texto_abnt,
                     "metadado": match.metadata,
                     "tipo": "ABNT",
                     "score": match.score
                 })
    except Exception as e:
        print(f"Erro na busca ABNT: {e}")
    
    try:
        # Busca no namespace padrão (leis)
        leis_response = pinecone_index.query(
            vector=query_embedding,
            top_k=5,
            namespace="",
            include_metadata=True
        )
        
        for match in leis_response.matches:
             if match.score > 0.3:  # Filtro de relevância mais permissivo
                 leis_results.append({
                     "texto": match.metadata.get('conteudo', match.metadata.get('content', '')),
                     "metadado": match.metadata,
                     "tipo": "LEI",
                     "score": match.score
                 })
    except Exception as e:
        print(f"Erro na busca leis: {e}")
    
    # Combina e ordena resultados por score
    all_results = abnt_results + leis_results + coema_results
    all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return all_results[:top_k]

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
                **{k: v for k, v in {
                    "numero_lei": item["metadata"].get("numero_lei"),
                    "numero_lei_puro": item["metadata"].get("numero_lei_puro"),
                    "source": item["metadata"].get("source"),
                    "url": item["metadata"].get("url"),
                    "type": item["metadata"].get("type"),
                    "collected_at": item["metadata"].get("collected_at"),
                    "chunk_index": item["metadata"].get("chunk_index"),
                    "total_chunks": item["metadata"].get("total_chunks")
                }.items() if v is not None}
            }
        )
        for item in itens
    ]

    vectorstore.add_documents(documentos)
    print(f"{len(documentos)} documentos enviados ao Pinecone com sucesso.")
