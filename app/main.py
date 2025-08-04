from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import query, importar, consulta

app = FastAPI(title="API Leis Ambientais")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para a página inicial
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

app.include_router(query.router)
app.include_router(importar.router)
app.include_router(consulta.router)