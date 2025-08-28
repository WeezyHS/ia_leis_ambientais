# --- Importações ---
from fastapi import FastAPI, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from app.routes import query, importar, consulta, multi_sources, coema, auth, documents
from app.services.document_chat_service import DocumentChatService
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import openai
import pandas as pd
import json
from io import BytesIO

from typing import List, Optional, Dict, Any
from uuid import UUID

# Adicionar o diretório tabela_generator ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tabela_generator'))
from ia_tabela_service import IATabela

load_dotenv()

STREAMLIT_URL = os.getenv("STREAMLIT_URL", "")

class UserLogin(BaseModel):
    email: str
    password: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    conversation_id: Optional[UUID] = None # O ID é opcional

class TabelaRequest(BaseModel):
    descricao: str
    municipio: Optional[str] = None
    atividade: Optional[str] = None
    esferas: List[str] = ["federal", "estadual", "municipal"]
    max_documentos: int = 50
    formato: str = "excel"

class QuadroResumoRequest(BaseModel):
    descricao: str
    municipio: Optional[str] = None
    atividade: Optional[str] = None
    esferas: List[str] = ["federal", "estadual", "municipal"]
    max_documentos: int = 20

app = FastAPI(
    title="API Leis Ambientais",
    description="Sistema de consulta a leis ambientais com múltiplas fontes de dados"
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

openai.api_key = os.environ.get("OPENAI_API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/teste-static", StaticFiles(directory="TESTE_chat_o3_e_o3-mini_Rogerio"), name="teste-static")

# Incluir rotas de documentos
app.include_router(documents.router, prefix="/documents", tags=["documents"])

@app.get("/dashboard")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/user-chats")
async def get_user_chats():
    test_user_id = "ca9520b0-2cd7-4e6f-b8d2-8b6e805188b7"  # Simulado para dev/teste

    try:
        response = supabase \
            .table("conversations") \
            .select("*") \
            .eq("user_id", test_user_id) \
            .order("created_at", desc=True) \
            .execute()

        return JSONResponse(content=response.data)

    except Exception as e:
        print(f"Erro ao buscar chats: {e}")
        return JSONResponse(status_code=500, content={"message": "Erro ao buscar conversas."})

@app.get("/chat/{conversation_id}/messages")
async def get_chat_messages(conversation_id: str):
    try:
        response = supabase \
            .table("messages") \
            .select("role, content") \
            .eq("conversation_id", conversation_id) \
            .order("created_at", desc=False) \
            .execute()

        return JSONResponse(content=response.data)

    except Exception as e:
        print(f"Erro ao buscar mensagens: {e}")
        return JSONResponse(status_code=500, content={"message": "Erro ao buscar mensagens."})

@app.get("/")
async def serve_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat-ai")
async def serve_chat_page(request: Request):
    return templates.TemplateResponse("IA_chat.html", {"request": request})



@app.get("/teste-o3-completo")
async def teste_o3_completo(request: Request):
    """Página de teste completa para modelo o3 com persistência"""
    return FileResponse("TESTE_chat_o3_e_o3-mini_Rogerio/chat_o3_completo.html")

# Em vez do RedirectResponse externo, deveria ser algo como:
@app.get("/gerador-tabelas")
async def serve_gerador_tabelas(request: Request):
    """Serve a nova interface HTML do gerador de tabelas"""
    return templates.TemplateResponse("gerador_tabelas.html", {"request": request})

@app.get("/api/fontes-dados")
async def get_fontes_dados():
    """Retorna contadores das fontes de dados disponíveis"""
    try:
        ia_tabela = IATabela()
        dados = ia_tabela.todas_fontes_data

        # Contar por jurisdição
        federais = len([d for d in dados if d.get('jurisdicao', '').startswith('Federal')])
        estaduais = len([d for d in dados if d.get('jurisdicao', '').startswith('Estadual')])
        municipais = len([d for d in dados if d.get('jurisdicao', '').startswith('Municipal')])
        total = len(dados)
        
        return JSONResponse(content={
            "federais": federais,
            "estaduais": estaduais,
            "municipais": municipais,
            "total": total
        })
    except Exception as e:
        print(f"Erro ao carregar fontes de dados: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro ao carregar dados"})

@app.post("/api/gerar-estrutura")
async def gerar_estrutura_tabela(request: TabelaRequest):
    """Gera estrutura de tabela baseada na descrição do usuário"""
    try:
        ia_tabela = IATabela()
        
        # Gerar estrutura usando IA
        estrutura = ia_tabela.gerar_estrutura_tabela(request.descricao)
        
        # Popular tabela com dados
        incluir_todas_fontes = len(request.esferas) > 1 or "federal" in request.esferas
        df_populado = ia_tabela.popular_tabela(estrutura, request.max_documentos, incluir_todas_fontes)
        
        # Converter DataFrame para formato JSON
        dados_tabela = df_populado.to_dict('records')
        colunas = list(df_populado.columns)
        
        return JSONResponse(content={
            "estrutura": estrutura,
            "dados": dados_tabela,
            "colunas": colunas,
            "total_linhas": len(df_populado),
            "estatisticas": {
                "documentos_processados": len(df_populado),
                "colunas_geradas": len(colunas),
                "esferas_incluidas": request.esferas
            }
        })
        
    except Exception as e:
        print(f"Erro ao gerar estrutura: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro ao gerar estrutura: {str(e)}"})

@app.post("/api/gerar-quadro-resumo")
async def gerar_quadro_resumo(request: QuadroResumoRequest):
    """Gera quadro-resumo simplificado das legislações"""
    try:
        ia_tabela = IATabela()
        
        # Estrutura simplificada para quadro-resumo
        estrutura_resumo = {
            "titulo_tabela": "Quadro-Resumo de Legislação Ambiental",
            "descricao": "Resumo das principais legislações aplicáveis",
            "colunas": [
                {"nome": "legislacao", "tipo": "texto", "descricao": "Nome da legislação"},
                {"nome": "esfera", "tipo": "texto", "descricao": "Esfera (Federal/Estadual/Municipal)"},
                {"nome": "tema", "tipo": "texto", "descricao": "Tema principal"},
                {"nome": "aplicabilidade", "tipo": "texto", "descricao": "Aplicabilidade ao projeto"}
            ],
            "filtros_sugeridos": ["esfera", "tema"],
            "ordenacao_padrao": "esfera"
        }
        
        # Popular com dados reduzidos
        incluir_todas_fontes = len(request.esferas) > 1 or "federal" in request.esferas
        df_populado = ia_tabela.popular_tabela(estrutura_resumo, request.max_documentos, incluir_todas_fontes)
        
        # Converter para formato JSON
        dados_tabela = df_populado.to_dict('records')
        colunas = list(df_populado.columns)
        
        return JSONResponse(content={
            "estrutura": estrutura_resumo,
            "dados": dados_tabela,
            "colunas": colunas,
            "total_linhas": len(df_populado),
            "estatisticas": {
                "documentos_processados": len(df_populado),
                "tipo": "quadro_resumo",
                "esferas_incluidas": request.esferas
            }
        })
        
    except Exception as e:
        print(f"Erro ao gerar quadro-resumo: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro ao gerar quadro-resumo: {str(e)}"})

@app.post("/api/download-tabela")
async def download_tabela(request: dict = Body(...)):
    """Gera e retorna arquivo para download (Excel ou CSV)"""
    try:
        from fastapi.responses import StreamingResponse
        import tempfile
        
        dados = request.get('dados', [])
        formato = request.get('formato', 'excel')
        nome_arquivo = request.get('nome_arquivo', 'tabela_legislacao')
        
        if not dados:
            return JSONResponse(status_code=400, content={"error": "Nenhum dado fornecido"})
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        if formato.lower() == 'excel':
            # Gerar Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Legislação Ambiental', index=False)
            output.seek(0)
            
            return StreamingResponse(
                BytesIO(output.getvalue()),
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={"Content-Disposition": f"attachment; filename={nome_arquivo}.xlsx"}
            )
        else:
            # Gerar CSV
            output = BytesIO()
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            output.write(csv_data.encode('utf-8-sig'))
            output.seek(0)
            
            return StreamingResponse(
                BytesIO(output.getvalue()),
                media_type='text/csv',
                headers={"Content-Disposition": f"attachment; filename={nome_arquivo}.csv"}
            )
            
    except Exception as e:
        print(f"Erro ao gerar download: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro ao gerar arquivo: {str(e)}"})

@app.post("/login")
async def handle_login(user_login: UserLogin):
    try:
        session = supabase.auth.sign_in_with_password({"email": user_login.email, "password": user_login.password})
        return JSONResponse(status_code=200, content={"message": "Login realizado com sucesso!", "user_id": session.user.id})
    except Exception as e:
        return JSONResponse(status_code=401, content={"message": "Email ou senha incorretos."})

@app.patch("/chat/{conversation_id}")
async def update_chat_title(conversation_id: str, data: dict = Body(...)):
    new_title = data.get("title")
    if not new_title:
        return JSONResponse(status_code=400, content={"message": "Título não fornecido"})

    try:
        supabase \
            .table("conversations") \
            .update({"title": new_title}) \
            .eq("id", conversation_id) \
            .execute()
        
        return JSONResponse(status_code=200, content={"message": "Título atualizado com sucesso"})
    
    except Exception as e:
        print(f"Erro ao atualizar título: {e}")
        return JSONResponse(status_code=500, content={"message": "Erro ao atualizar título"})

@app.delete("/chat/{conversation_id}")
async def delete_chat(conversation_id: str):
    try:
        # Primeiro exclui todas as mensagens da conversa
        supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()
        
        # Depois exclui a conversa
        supabase.table("conversations").delete().eq("id", conversation_id).execute()
        
        return JSONResponse(
            status_code=200,
            content={"message": "Chat excluído com sucesso"}
        )
    except Exception as e:
        print(f"Erro ao excluir chat: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Erro ao excluir chat"}
        )

@app.post("/ask-ia")
async def ask_ia(chat_request: ChatRequest):
    # 1) Converte o histórico em dicts simples
    conversation_history = [message.dict() for message in chat_request.history]
    user_message = conversation_history[-1]['content']

    # 2) Converte conversation_id vindo do request para string (se existir)
    conversation_id = None
    if chat_request.conversation_id is not None:
        # chat_request.conversation_id é UUID por causa do Pydantic
        conversation_id = str(chat_request.conversation_id)

    test_user_id = "ca9520b0-2cd7-4e6f-b8d2-8b6e805188b7"

    try:
        # 3) Se não veio id, cria a conversa e já padroniza para string
        if conversation_id is None:
            new_conv = supabase.table("conversations").insert({
                "user_id": test_user_id,
                "title": user_message[:50]
            }).execute()
            conv_id = new_conv.data[0]["id"]
            conversation_id = str(conv_id)  # <- padroniza AQUI

        # 4) Verificar se há documento associado a esta conversa e incluir contexto
        enhanced_messages = conversation_history.copy()
        
        # Buscar contexto do documento associado a esta conversa específica
        document_context = DocumentChatService.get_latest_document_context(conversation_id, user_message)
        
        if document_context:
            # Modificar a última mensagem do usuário para incluir contexto
            enhanced_messages[-1]['content'] = user_message + document_context

        # 5) Chama a OpenAI com mensagens aprimoradas
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=enhanced_messages
        )
        ai_response = completion.choices[0].message.content

        # 5) Ao salvar mensagens no Supabase, use SEMPRE string no conversation_id
        supabase.table("messages").insert([
            {"conversation_id": conversation_id, "role": "user", "content": user_message},
            {"conversation_id": conversation_id, "role": "assistant", "content": ai_response}
        ]).execute()

        return JSONResponse(
            status_code=200,
            content={"response": ai_response, "conversation_id": conversation_id}
        )

    except Exception as e:
        # Esse erro pode vir tanto da OpenAI quanto do Supabase (serialização)
        print(f"Erro no processamento do chat: {e}")
        return JSONResponse(
            status_code=500,
            content={"response": "Desculpe, ocorreu um erro ao comunicar com a IA."}
        )

@app.post("/ask-ia-o3")
async def ask_ia_o3(chat_request: ChatRequest):
    """Endpoint para testar modelo o3 com persistência completa"""
    # 1) Converte o histórico em dicts simples
    conversation_history = [message.dict() for message in chat_request.history]
    user_message = conversation_history[-1]['content']

    # 2) Converte conversation_id vindo do request para string (se existir)
    conversation_id = None
    if chat_request.conversation_id is not None:
        # chat_request.conversation_id é UUID por causa do Pydantic
        conversation_id = str(chat_request.conversation_id)

    test_user_id = "ca9520b0-2cd7-4e6f-b8d2-8b6e805188b7"

    try:
        # 3) Se não veio id, cria a conversa e já padroniza para string
        if conversation_id is None:
            new_conv = supabase.table("conversations").insert({
                "user_id": test_user_id,
                "title": user_message[:50]
            }).execute()
            conv_id = new_conv.data[0]["id"]
            conversation_id = str(conv_id)  # <- padroniza AQUI

        # 4) Verificar se há documento associado a esta conversa e incluir contexto
        enhanced_messages = conversation_history.copy()
        
        # Buscar contexto do documento associado a esta conversa específica
        document_context = DocumentChatService.get_latest_document_context(conversation_id, user_message)
        
        if document_context:
            # Modificar a última mensagem do usuário para incluir contexto
            enhanced_messages[-1]['content'] = user_message + document_context

        # 5) Chama a OpenAI com modelo o3
        completion = openai.chat.completions.create(
            model="o3",
            messages=enhanced_messages
        )
        ai_response = completion.choices[0].message.content

        # 6) Ao salvar mensagens no Supabase, use SEMPRE string no conversation_id
        supabase.table("messages").insert([
            {"conversation_id": conversation_id, "role": "user", "content": user_message},
            {"conversation_id": conversation_id, "role": "assistant", "content": ai_response}
        ]).execute()

        return JSONResponse(
            status_code=200,
            content={"response": ai_response, "conversation_id": conversation_id}
        )

    except Exception as e:
        # Esse erro pode vir tanto da OpenAI quanto do Supabase (serialização)
        print(f"Erro no processamento do chat o3: {e}")
        return JSONResponse(
            status_code=500,
            content={"response": "Desculpe, ocorreu um erro ao comunicar com o modelo o3."}
        )



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # <- lê do ambiente
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)