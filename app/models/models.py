from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChunkedDocument(BaseModel):
    """Modelo para documentos divididos em chunks"""
    filename: str
    chunks: List[str]

class QueryRequest(BaseModel):
    """Modelo para requisições de consulta"""
    texto: str