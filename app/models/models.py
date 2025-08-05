from pydantic import BaseModel
from typing import List

class ChunkedDocument(BaseModel):
    """Modelo para documentos divididos em chunks"""
    filename: str
    chunks: List[str]

class QueryRequest(BaseModel):
    """Modelo para requisições de consulta"""
    texto: str