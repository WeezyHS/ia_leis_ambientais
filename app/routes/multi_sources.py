"""
Rotas para gerenciamento de múltiplas fontes de dados
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import json
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from multi_source_indexer import MultiSourceIndexer
    from app.services.multi_source_scraper import MultiSourceCollector
except ImportError as e:
    print(f"Aviso: Sistema de múltiplas fontes não disponível: {e}")
    MultiSourceIndexer = None
    MultiSourceCollector = None

router = APIRouter()

class CustomDocument(BaseModel):
    source: str
    url: str
    text: str
    type: str = "html"
    titulo: Optional[str] = None
    categoria: Optional[str] = None

class AddCustomSourceRequest(BaseModel):
    documents: List[CustomDocument]

class CollectFromSourcesRequest(BaseModel):
    sources: Optional[List[str]] = None  # Se None, coleta de todas as fontes

@router.post("/multi-sources/add-custom")
async def add_custom_documents(request: AddCustomSourceRequest, background_tasks: BackgroundTasks):
    """Adiciona documentos personalizados ao índice"""
    
    if not MultiSourceIndexer:
        raise HTTPException(status_code=500, detail="Sistema de múltiplas fontes não disponível")
    
    try:
        # Converte os documentos para o formato esperado
        documents = []
        for doc in request.documents:
            documents.append({
                'source': doc.source,
                'url': doc.url,
                'text': doc.text,
                'type': doc.type,
                'collected_at': datetime.now().isoformat(),
                'titulo': doc.titulo,
                'categoria': doc.categoria
            })
        
        # Adiciona a indexação como tarefa em background
        background_tasks.add_task(index_custom_documents, documents)
        
        return {
            "status": "success",
            "message": f"Iniciada indexação de {len(documents)} documentos",
            "documents_count": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar documentos: {str(e)}")

@router.post("/multi-sources/collect")
async def collect_from_sources(request: CollectFromSourcesRequest, background_tasks: BackgroundTasks):
    """Coleta dados de múltiplas fontes configuradas"""
    
    if not MultiSourceCollector:
        raise HTTPException(status_code=500, detail="Sistema de múltiplas fontes não disponível")
    
    try:
        # Adiciona a coleta como tarefa em background
        background_tasks.add_task(collect_and_index_sources, request.sources)
        
        sources_msg = "todas as fontes" if not request.sources else f"fontes: {', '.join(request.sources)}"
        
        return {
            "status": "success",
            "message": f"Iniciada coleta de dados de {sources_msg}",
            "sources": request.sources or "all"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar coleta: {str(e)}")

@router.get("/multi-sources/status")
async def get_sources_status():
    """Retorna o status das fontes disponíveis"""
    
    if not MultiSourceCollector:
        return {
            "status": "unavailable",
            "message": "Sistema de múltiplas fontes não disponível",
            "sources": []
        }
    
    try:
        collector = MultiSourceCollector()
        available_sources = [scraper.name for scraper in collector.scrapers]
        
        return {
            "status": "available",
            "sources": available_sources,
            "total_sources": len(available_sources)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao verificar status: {str(e)}",
            "sources": []
        }

@router.post("/multi-sources/add-url")
async def add_from_url(url: str, source_name: str, background_tasks: BackgroundTasks):
    """Adiciona um documento a partir de uma URL"""
    
    if not MultiSourceIndexer:
        raise HTTPException(status_code=500, detail="Sistema de múltiplas fontes não disponível")
    
    try:
        # Adiciona a indexação por URL como tarefa em background
        background_tasks.add_task(index_from_url, url, source_name)
        
        return {
            "status": "success",
            "message": f"Iniciada indexação do documento de {url}",
            "url": url,
            "source": source_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar URL: {str(e)}")

# Funções auxiliares para tarefas em background

async def index_custom_documents(documents: List[dict]):
    """Indexa documentos personalizados em background"""
    try:
        indexer = MultiSourceIndexer()
        indexer.add_custom_source("Custom", documents)
        print(f"✅ Indexados {len(documents)} documentos personalizados")
    except Exception as e:
        print(f"❌ Erro na indexação de documentos personalizados: {e}")

async def collect_and_index_sources(sources: Optional[List[str]]):
    """Coleta e indexa dados de múltiplas fontes em background"""
    try:
        collector = MultiSourceCollector()
        indexer = MultiSourceIndexer()
        
        if sources:
            # Coleta apenas das fontes especificadas
            all_documents = []
            for source in sources:
                # Busca o scraper pelo nome
                scraper = next((s for s in collector.scrapers if s.name == source), None)
                if scraper:
                    documents = scraper.extract_documents()
                    all_documents.extend(documents)
                    print(f"✅ Coletados {len(documents)} documentos de {source}")
        else:
            # Coleta de todas as fontes
            all_documents = collector.collect_all_sources()
            print(f"✅ Coletados {len(all_documents)} documentos de todas as fontes")
        
        # Indexa os documentos coletados
        if all_documents:
            indexer.index_documents(all_documents)
            print(f"✅ Indexados {len(all_documents)} documentos no total")
        
    except Exception as e:
        print(f"❌ Erro na coleta e indexação: {e}")

async def index_from_url(url: str, source_name: str):
    """Indexa documento de uma URL em background"""
    try:
        indexer = MultiSourceIndexer()
        indexer.add_from_url(url, source_name)
        print(f"✅ Indexado documento de {url}")
    except Exception as e:
        print(f"❌ Erro na indexação de URL {url}: {e}")