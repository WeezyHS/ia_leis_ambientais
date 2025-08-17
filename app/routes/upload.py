from fastapi import APIRouter, HTTPException
# from fastapi import UploadFile, File  # Comentado temporariamente
from app.services import pdf_service

router = APIRouter()

# Rota temporariamente comentada devido ao problema com python-multipart
# @router.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="O arquivo precisa ser um PDF.")
# 
#     content = await file.read()
#     text = pdf_service.extract_text_from_pdf(content)
# 
#     if not text.strip():
#         raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")
# 
#     chunks = pdf_service.chunk_text(text)
# 
#     return {
#         "filename": file.filename,
#         "quantidade_chunks": len(chunks),
#         "primeiros_chunks": chunks[:3]  # só para exibir os primeiros como teste
#     }
