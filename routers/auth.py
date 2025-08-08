from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from database import session_local, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
    prefix = '/auth', 
    tags = ['Auth']
)

SECRET_KEY = "long_string"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl='Auth/login',
    scheme_name="JWT"
)

class CreateUserRequest(BaseModel):
    username: str
    email: str 
    first_name: str
    last_name: str
    password: str
    role: str = 'user'

class Token(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str
    
class AccessToken(BaseModel):
    access_token:str
    token_type:str
    
def get_db():
    db = session_local()
    try:
        yield db 
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db: Session):
    """Autentica usuário usando query SQL direta"""
    print(f"[DEBUG] Iniciando autenticação para usuário: {username}")
    
    try:
        # Query SQL direta usando os mesmos campos do insert
        result = db.execute(
            text("SELECT ID, USERNAME, HASHED_PASSWORD FROM DB_SCRAPE.SC_SCRAPE.USERS WHERE USERNAME = :username AND IS_ACTIVE = TRUE"),
            {"username": username}
        )
        user_data = result.fetchone()
        
        if not user_data:
            print(f"[DEBUG] Usuário não encontrado: {username}")
            # Tentar buscar todos os usuários para debug
            all_users = db.execute(text("SELECT USERNAME FROM DB_SCRAPE.SC_SCRAPE.USERS LIMIT 5")).fetchall()
            print(f"[DEBUG] Usuários encontrados na tabela: {[row[0] for row in all_users]}")
            return False
        
        # Acessar colunas por índice para evitar problemas de case
        user_id = user_data[0]      # ID
        user_username = user_data[1] # USERNAME  
        user_password = user_data[2] # HASHED_PASSWORD
        
        print(f"[DEBUG] Usuário encontrado: {user_username}, ID: {user_id}")
        
        # Verificar senha
        password_valid = bcrypt_context.verify(password, user_password)
        print(f"[DEBUG] Verificação de senha para {username}: {'Válida' if password_valid else 'Inválida'}")
        
        if not password_valid:
            return False
        
        print(f"[DEBUG] Autenticação bem-sucedida para: {username}")
        
        # Retorna dicionário com dados do usuário
        return {
            "id": user_id,
            "username": user_username
        }
        
    except Exception as e:
        print(f"[ERROR] Erro na autenticação: {str(e)}")
        return False 

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode["exp"] = int(expires.timestamp())
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # Decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extrai as informações
        username = payload.get('sub')
        user_id = payload.get('id')
        
        # Valida as informações
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - dados de usuário ausentes'
            )
        
        return {'username': username, 'id': user_id}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Token inválido ou expirado: {str(e)}'
        )

@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: CreateUserRequest, db: db_dependency):
    """Criar usuário usando INSERT direto no Snowflake"""
    
    # Verificar se usuário já existe
    check_user = db.execute(
        text("SELECT USERNAME FROM DB_SCRAPE.SC_SCRAPE.USERS WHERE USERNAME = :username OR EMAIL = :email"),
        {"username": user_request.username, "email": user_request.email}
    ).fetchone()
    
    if check_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ou email já existe"
        )
    
    # Hash da senha
    hashed_password = bcrypt_context.hash(user_request.password)
    
    # Inserir usuário
    try:
        db.execute(
            text("""
                INSERT INTO DB_SCRAPE.SC_SCRAPE.USERS (EMAIL, USERNAME, FIRST_NAME, LAST_NAME, HASHED_PASSWORD, IS_ACTIVE, ROLE)
                VALUES (:email, :username, :first_name, :last_name, :hashed_password, TRUE, :role)
            """),
            {
                "email": user_request.email,
                "username": user_request.username,
                "first_name": user_request.first_name,
                "last_name": user_request.last_name,
                "hashed_password": hashed_password,
                "role": user_request.role
            }
        )
        db.commit()
        return {"message": "Usuário criado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    print(f"[DEBUG] Tentativa de login para usuário: {form_data.username}")
    user = authenticate_user(str(form_data.username), str(form_data.password), db)
    if not user:
        print(f"[DEBUG] Falha na autenticação para: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Could not validate the user")
    print(f"[DEBUG] Login bem-sucedido para: {user['username']}")
    access_token = create_access_token(user["username"], user["id"], timedelta(minutes=20))
    refresh_token = create_access_token(user["username"], user["id"], timedelta(days=7))
    return {'access_token': access_token, 
            'refresh_token': refresh_token, 
            'token_type': 'bearer'}

@router.post("/refresh", response_model=AccessToken)
async def refresh_token(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail='Invalid token')
    new_access_token = create_access_token(current_user['username'],
                                       current_user['id'], timedelta(minutes=20))
    return {"access_token": new_access_token, "token_type": "bearer"}  