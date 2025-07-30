from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import leis_html_service

router = APIRouter()

@router.post("/importar-leis")
async def importar_leis_html(file: UploadFile = File(...)):
    if not file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="O arquivo precisa ser um HTML.")

    html_content = await file.read()
    try:
        leis = leis_html_service.extrair_leis_do_html(html_content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar HTML: {str(e)}")

    if not leis:
        raise HTTPException(status_code=400, detail="Nenhuma lei encontrada no HTML.")

    return {
        "quantidade_leis": len(leis),
        "exemplo": leis[:3]  # Mostra as 3 primeiras leis extraídas
    }
