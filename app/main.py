from fastapi import FastAPI
from app.routes import query, importar, consulta

app = FastAPI(title="API Leis Ambientais")

app.include_router(query.router)
app.include_router(importar.router)
app.include_router(consulta.router)