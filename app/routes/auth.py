from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    verify_token,
    get_user_by_email
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Modelos Pydantic para requisições
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    expires_in: int

class TokenVerifyResponse(BaseModel):
    valid: bool
    user_email: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: str

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Rota de login que autentica o usuário e retorna um token JWT.
    
    Args:
        login_data: Dados de login (email, password, remember_me)
        db: Sessão do banco de dados
    
    Returns:
        LoginResponse: Token de acesso e informações do usuário
    
    Raises:
        HTTPException: 401 se credenciais inválidas, 500 se erro interno
    """
    try:
        # Autenticar usuário
        user = authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Definir tempo de expiração baseado no "remember me"
        expires_minutes = 43200 if login_data.remember_me else 30  # 30 dias ou 30 minutos
        
        # Criar token de acesso
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta_minutes=expires_minutes
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_email=user.email,
            expires_in=expires_minutes * 60  # Retornar em segundos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token_route(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Rota para verificar se um token JWT é válido.
    
    Args:
        credentials: Credenciais HTTP Bearer com o token
        db: Sessão do banco de dados
    
    Returns:
        TokenVerifyResponse: Status de validade do token e informações do usuário
    """
    try:
        token = credentials.credentials
        
        # Verificar token
        payload = verify_token(token)
        
        if payload is None:
            return TokenVerifyResponse(
                valid=False,
                message="Token inválido ou expirado"
            )
        
        user_email = payload.get("sub")
        
        # Verificar se o usuário ainda existe e está ativo
        user = get_user_by_email(db, user_email)
        
        if not user or not user.is_active:
            return TokenVerifyResponse(
                valid=False,
                message="Usuário não encontrado ou inativo"
            )
        
        return TokenVerifyResponse(
            valid=True,
            user_email=user_email,
            message="Token válido"
        )
        
    except Exception as e:
        return TokenVerifyResponse(
            valid=False,
            message=f"Erro ao verificar token: {str(e)}"
        )

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Rota para obter informações do usuário atual baseado no token.
    
    Args:
        credentials: Credenciais HTTP Bearer com o token
        db: Sessão do banco de dados
    
    Returns:
        dict: Informações do usuário atual
    
    Raises:
        HTTPException: 401 se token inválido
    """
    try:
        token = credentials.credentials
        
        # Verificar token
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_email = payload.get("sub")
        
        # Buscar usuário
        user = get_user_by_email(db, user_email)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

# Função auxiliar para obter usuário atual (para usar em outras rotas)
async def get_current_active_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Função auxiliar para obter o usuário atual ativo.
    Pode ser usada como dependência em outras rotas que precisam de autenticação.
    
    Args:
        credentials: Credenciais HTTP Bearer com o token
        db: Sessão do banco de dados
    
    Returns:
        User: Objeto do usuário atual
    
    Raises:
        HTTPException: 401 se token inválido ou usuário inativo
    """
    try:
        token = credentials.credentials
        
        # Verificar token
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_email = payload.get("sub")
        
        # Buscar usuário
        user = get_user_by_email(db, user_email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )