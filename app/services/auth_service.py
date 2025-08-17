from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.models import User
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui-mude-em-producao")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, expires_delta_minutes: Optional[int] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif expires_delta_minutes:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Autentica usuário"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str) -> User:
    """Cria novo usuário"""
    hashed_password = hash_password(password)
    user = User(
        email=email,
        password_hash=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user