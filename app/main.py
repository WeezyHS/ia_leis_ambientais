# --- Importações ---
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.routes import query, importar, consulta, multi_sources, coema, auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import openai

from typing import List, Optional
from uuid import UUID

load_dotenv()

class UserLogin(BaseModel):
    email: str
    password: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    conversation_id: Optional[UUID] = None # O ID é opcional

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

@app.get("/")
async def serve_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat-ai")
async def serve_chat_page(request: Request):
    return templates.TemplateResponse("IA_chat.html", {"request": request})

@app.post("/login")
async def handle_login(user_login: UserLogin):
    try:
        session = supabase.auth.sign_in_with_password({"email": user_login.email, "password": user_login.password})
        return JSONResponse(status_code=200, content={"message": "Login realizado com sucesso!", "user_id": session.user.id})
    except Exception as e:
        return JSONResponse(status_code=401, content={"message": "Email ou senha incorretos."})

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

        # 4) Chama a OpenAI normalmente (histórico só tem role/content)
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)