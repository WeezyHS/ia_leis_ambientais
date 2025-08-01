from fastapi import APIRouter
from pydantic import BaseModel
from app.services.consult_service import consultar_lei

router = APIRouter()

class ConsultaRequest(BaseModel):
    pergunta: str
    top_k: int = 5  # ainda não está sendo usado na IA, mas pode ser integrado

@router.post("/consulta")
def consultar_leis(request: ConsultaRequest):
    resultado = consultar_lei(request.pergunta)
    return {
        "resposta": resultado["resposta"],
        "leis_relacionadas": resultado["leis_relacionadas"]
    }
