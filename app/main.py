from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import query, importar, consulta, multi_sources, coema, auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Leis Ambientais", 
    description="Sistema de consulta a leis ambientais com múltiplas fontes de dados",
    timeout=120
)

# Adicione após criar a instância do FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servir arquivos do WeWeb
app.mount("/assets", StaticFiles(directory="static/weweb/assets"), name="weweb_assets")
app.mount("/fonts", StaticFiles(directory="static/weweb/fonts"), name="weweb_fonts")
app.mount("/data", StaticFiles(directory="static/weweb/data"), name="weweb_data")
app.mount("/icons", StaticFiles(directory="static/weweb/icons"), name="weweb_icons")
app.mount("/images", StaticFiles(directory="static/weweb/images"), name="weweb_images")

# Rota para servir o index.html do WeWeb na raiz
@app.get("/")
async def serve_weweb_index():
    return FileResponse("static/weweb/index.html")

# Rota para servir arquivos específicos do WeWeb
@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse("static/weweb/manifest.json")

@app.get("/serviceworker.js")
async def serve_serviceworker():
    return FileResponse("static/weweb/serviceworker.js")

@app.get("/robots.txt")
async def serve_robots():
    return FileResponse("static/weweb/robots.txt")

@app.get("/sitemap.xml")
async def serve_sitemap():
    return FileResponse("static/weweb/sitemap.xml")

@app.get("/favicon.ico")
async def serve_favicon():
    return FileResponse("static/weweb/favicon.ico")

# Rota para a página chat-ai do WeWeb
@app.get("/chat-ai")
async def serve_chat_ai():
    return FileResponse("static/weweb/index.html")

# Incluir outros routers
# Registrar rotas
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(importar.router)
app.include_router(consulta.router)
app.include_router(multi_sources.router)
app.include_router(coema.router)

# Criar tabelas do banco de dados
from app.database import create_tables
create_tables()