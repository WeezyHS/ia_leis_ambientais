from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import PDFService
from app.services.document_chat_service import DocumentChatService
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class ChatRequest(BaseModel):
    document_id: str
    message: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para upload e processamento de arquivos PDF
    """
    try:
        # Verificar se é um arquivo PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são suportados")
        
        # Ler o conteúdo do arquivo
        content = await file.read()
        
        # Processar o PDF
        chunks = PDFService.process_pdf(content)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF")
        
        # Gerar ID único para o documento
        document_id = DocumentChatService.generate_document_id()
        
        # Armazenar documento no serviço
        DocumentChatService.store_document(document_id, file.filename, chunks)
        
        return {
            "success": True,
            "message": "PDF processado com sucesso",
            "document_id": document_id,
            "filename": file.filename,
            "chunks_count": len(chunks),
            "preview": chunks[0][:200] + "..." if chunks[0] else "Sem conteúdo"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

@router.post("/chat")
async def chat_with_document(request: ChatRequest):
    """
    Endpoint para conversar com um documento carregado
    """
    try:
        # Verificar se o documento existe
        document = DocumentChatService.get_document(request.document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Construir prompt com contexto do documento
        context_prompt = DocumentChatService.build_context_prompt(
            request.document_id, 
            request.message
        )
        
        # Adicionar mensagem do usuário ao histórico
        DocumentChatService.add_chat_message(
            request.document_id, 
            "user", 
            request.message
        )
        
        # Aqui você integraria com seu serviço de IA preferido
        # Por simplicidade, retornamos uma resposta básica
        ai_response = f"Baseado no documento '{document['filename']}', posso ajudar com sua pergunta sobre: {request.message}"
        
        # Adicionar resposta da IA ao histórico
        DocumentChatService.add_chat_message(
            request.document_id, 
            "assistant", 
            ai_response
        )
        
        return {
            "response": ai_response,
            "document_id": request.document_id,
            "document_name": document['filename']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat com documento: {str(e)}")

@router.get("/list")
async def list_documents():
    """
    Endpoint para listar documentos carregados
    """
    try:
        documents = DocumentChatService.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")

@router.get("/{document_id}/history")
async def get_chat_history(document_id: str):
    """
    Endpoint para obter histórico de chat de um documento
    """
    try:
        document = DocumentChatService.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        history = DocumentChatService.get_chat_history(document_id)
        return {
            "document_id": document_id,
            "document_name": document['filename'],
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Endpoint para deletar um documento
    """
    try:
        success = DocumentChatService.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        return {"message": "Documento deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar documento: {str(e)}")

@router.get("/status")
async def get_status():
    """
    Endpoint para verificar status do serviço de upload
    """
    return {"status": "active", "service": "document_upload"}
