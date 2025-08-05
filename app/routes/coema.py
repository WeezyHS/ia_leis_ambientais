"""
Rotas para o COEMA (Conselho Estadual de Meio Ambiente)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from app.services.coema_service import COEMAService
from app.models.models import QueryRequest

router = APIRouter()
coema_service = COEMAService()

@router.post("/coema/index")
async def index_coema_documents(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Indexa documentos do COEMA no Pinecone
    """
    try:
        # Executa a indexação em background
        def index_task():
            return coema_service.index_coema_documents()
        
        background_tasks.add_task(index_task)
        
        return {
            "message": "Indexação dos documentos do COEMA iniciada em background",
            "status": "processing",
            "source": "COEMA"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar indexação do COEMA: {str(e)}")

@router.post("/coema/index/sync")
async def index_coema_documents_sync() -> Dict[str, Any]:
    """
    Indexa documentos do COEMA no Pinecone de forma síncrona
    """
    try:
        result = coema_service.index_coema_documents()
        
        if result['success']:
            return {
                "message": "Documentos do COEMA indexados com sucesso",
                "status": "completed",
                "indexed_documents": result['indexed_documents'],
                "total_documents": result['total_documents'],
                "total_chunks": result['total_chunks'],
                "namespace": result['namespace'],
                "errors": result.get('errors', [])
            }
        else:
            return {
                "message": "Falha na indexação dos documentos do COEMA",
                "status": "failed",
                "errors": result.get('errors', [])
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao indexar documentos do COEMA: {str(e)}")

@router.post("/coema/search")
async def search_coema(request: QueryRequest) -> Dict[str, Any]:
    """
    Busca documentos do COEMA
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query não pode estar vazia")
        
        # Busca documentos do COEMA
        results = coema_service.search_coema_documents(
            query=request.query,
            top_k=5
        )
        
        if not results:
            return {
                "message": "Nenhum documento do COEMA encontrado para a consulta",
                "query": request.query,
                "results": [],
                "source": "COEMA"
            }
        
        # Formata os resultados
        formatted_results = []
        for result in results:
            formatted_result = {
                "content": result['content'],
                "score": result['score'],
                "metadata": result['metadata'],
                "source": "COEMA"
            }
            formatted_results.append(formatted_result)
        
        return {
            "message": f"Encontrados {len(results)} documentos do COEMA",
            "query": request.query,
            "results": formatted_results,
            "source": "COEMA"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar no COEMA: {str(e)}")

@router.get("/coema/stats")
async def get_coema_stats() -> Dict[str, Any]:
    """
    Obtém estatísticas dos documentos do COEMA indexados
    """
    try:
        stats = coema_service.get_coema_statistics()
        
        return {
            "message": "Estatísticas do COEMA obtidas com sucesso",
            "stats": stats,
            "source": "COEMA"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas do COEMA: {str(e)}")

@router.delete("/coema/index")
async def delete_coema_index() -> Dict[str, Any]:
    """
    Remove todos os documentos do COEMA do índice
    """
    try:
        success = coema_service.delete_coema_index()
        
        if success:
            return {
                "message": "Índice do COEMA removido com sucesso",
                "status": "deleted",
                "source": "COEMA"
            }
        else:
            return {
                "message": "Falha ao remover índice do COEMA",
                "status": "failed",
                "source": "COEMA"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover índice do COEMA: {str(e)}")

@router.get("/coema/documents")
async def list_coema_documents() -> Dict[str, Any]:
    """
    Lista documentos do COEMA disponíveis
    """
    try:
        documents = coema_service.load_coema_documents()
        
        # Cria resumo dos documentos
        document_summary = []
        for i, doc in enumerate(documents):
            summary = {
                "index": i,
                "title": doc.get('title', 'Sem título')[:100],
                "type": doc.get('type', 'documento'),
                "year": doc.get('year', ''),
                "content_length": len(doc.get('content', '')),
                "url": doc.get('url', ''),
                "extracted_at": doc.get('extracted_at', '')
            }
            document_summary.append(summary)
        
        return {
            "message": f"Encontrados {len(documents)} documentos do COEMA",
            "total_documents": len(documents),
            "documents": document_summary,
            "source": "COEMA"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos do COEMA: {str(e)}")

@router.get("/coema/document/{doc_index}")
async def get_coema_document(doc_index: int) -> Dict[str, Any]:
    """
    Obtém um documento específico do COEMA pelo índice
    """
    try:
        documents = coema_service.load_coema_documents()
        
        if doc_index < 0 or doc_index >= len(documents):
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        document = documents[doc_index]
        
        return {
            "message": "Documento do COEMA encontrado",
            "document": document,
            "index": doc_index,
            "source": "COEMA"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter documento do COEMA: {str(e)}")

@router.get("/coema/info")
async def get_coema_info() -> Dict[str, Any]:
    """
    Obtém informações sobre o COEMA
    """
    return {
        "name": "COEMA - Conselho Estadual de Meio Ambiente",
        "description": "Conselho Estadual de Meio Ambiente do Tocantins",
        "website": "https://www.to.gov.br/semarh/conselhos/34qnn4fkmozg",
        "documents_types": [
            "Atas de reuniões",
            "Resoluções",
            "Portarias", 
            "Deliberações",
            "Boletins de desmatamento",
            "Documentos normativos"
        ],
        "data_source": "Site oficial da SEMARH-TO",
        "last_update": "2025-08-05",
        "namespace": "coema",
        "source": "COEMA"
    }