from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import session_local, Base, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from models import Users, Base
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
    prefix = '/auth', 
    tags = ['auth']
)



SECRET_KEY = "long_string"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl='auth/login',
    scheme_name="JWT"
)

class CreateUserRequest(BaseModel):
    username: str
    email:str 
    first_name:str
    last_name:str
    password:str
    role:str

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

def authenticate_user(username:str, password:str, db:Session):
    user = db.query(Users).filter(Users.username ==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user 

def create_access_token(username:str, user_id:int, expires_delta:timedelta):
    encode = {"sub":username, "id":user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)

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
    
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user_request:CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email, 
        username = create_user_request.username, 
        first_name = create_user_request.first_name, 
        last_name = create_user_request.last_name, 
        hashed_password = bcrypt_context.hash(create_user_request.password), 
        is_active = True
    )
    
    db.add(create_user_model)
    db.commit()
    
@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail = "Could not validate the user")
    access_token = create_access_token(user.username, user.id , timedelta(minutes=20))
    refresh_token = create_access_token(user.username, user.id, timedelta(days=7))
    return {'access_token': access_token, 
            'refresh_token': refresh_token, 
            'token_type':'bearer'}

@router.post("/refresh", response_model = AccessToken)
async def refresh_token(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail='Invalid token')
    new_access_token = create_access_token(current_user['username'],
                                       current_user['id'], timedelta(minutes=20))
    return {"access_token":new_access_token, "token_type":"bearer"}

@router.delete("/{user_id}")
async def delete_user(user_id :int, db: db_dependency):
    """
    Deleta um usuário pelo ID
    
    Parameters
    ----------
    user_id : int
        ID do usuário a ser deletado
    
    Raises
    ------
    HTTPException
        Se o usuário não for encontrado ou se ocorrer um erro ao deletar
    
    Returns
    -------
    Mensagem de sucesso ou erro
    """
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Usuário deletado com sucesso"}  