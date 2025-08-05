from fastapi import APIRouter
from app.models.models import QueryRequest
from app.services.pinecone_service import search_similar_documents

router = APIRouter(prefix="/busca", tags=["Busca Semântica"])

@router.post("/")
def buscar_similares(query: QueryRequest):
    resultados = search_similar_documents(query.texto, top_k=5)
    return {"resultados": resultados}
