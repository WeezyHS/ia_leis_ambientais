from fastapi import APIRouter
from pydantic import BaseModel
from app.services import pinecone_service

router = APIRouter()

class ConsultaRequest(BaseModel):
    pergunta: str
    top_k: int = 5  # opcional, padrão é 5 resultados

@router.post("/consulta")
def consultar_leis(request: ConsultaRequest):
    resultados = pinecone_service.search_similar_documents(
        texto=request.pergunta,
        top_k=request.top_k
    )
    return {"resultados": resultados}
