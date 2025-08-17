from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL do banco de dados - Supabase PostgreSQL ou SQLite como fallback
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback para SQLite se não houver configuração do Supabase
    DATABASE_URL = "sqlite:///./leis_ambientais.db"

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Criar engine do SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Configuração para SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Necessário para SQLite
    )
else:
    # Configuração para PostgreSQL (Supabase)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_recycle=300,    # Recicla conexões a cada 5 minutos
    )

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependência para obter sessão do banco de dados.
    Usado nas rotas FastAPI como dependência.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Cria todas as tabelas no banco de dados.
    """
    from app.models.models import Base
    Base.metadata.create_all(bind=engine)