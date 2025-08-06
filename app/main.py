from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import query, importar, consulta, multi_sources, coema
import uvicorn

app = FastAPI(
    title="API Leis Ambientais", 
    description="Sistema de consulta a leis ambientais com múltiplas fontes de dados",
    timeout=120
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para a página inicial
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

app.include_router(query.router)
app.include_router(importar.router)
app.include_router(consulta.router)
app.include_router(multi_sources.router)
app.include_router(coema.router)