from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.consult_service import consultar_lei
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

router = APIRouter()

class ConsultaRequest(BaseModel):
    pergunta: str
    top_k: int = 5  # ainda não está sendo usado na IA, mas pode ser integrado

# Pool de threads para operações assíncronas
executor = ThreadPoolExecutor(max_workers=4)

async def processar_consulta_async(pergunta: str):
    """Processa consulta de forma assíncrona"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, consultar_lei, pergunta)

@router.post("/consulta")
async def consultar_leis(request: ConsultaRequest):
    start_time = time.time()
    
    try:
        # Processa a consulta de forma assíncrona
        resultado = await processar_consulta_async(request.pergunta)
        
        processing_time = time.time() - start_time
        
        return {
            "resposta": resultado["resposta"],
            "leis_relacionadas": resultado["leis_relacionadas"],
            "tempo_processamento": f"{processing_time:.2f}s",
            "status": "sucesso"
        }
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "resposta": f"Erro ao processar consulta: {str(e)}",
            "leis_relacionadas": [],
            "tempo_processamento": f"{processing_time:.2f}s",
            "status": "erro"
        }
