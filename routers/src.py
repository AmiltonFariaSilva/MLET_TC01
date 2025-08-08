from pathlib import Path
from fastapi import HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Books, Base
from starlette import status
from typing import Optional, Annotated
from database import session_local, engine
from routers.auth import get_current_user, router as auth_router
from fastapi.routing import APIRouter

#Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/api/v1/Default",
    tags=["Default"]
)


# Carregar os dados do CSV

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOKS_CSV_PATH = PROJECT_ROOT / "data" / "books.csv"


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/")
async def root():
    """
    Mensagem inicial da api

    Returns
    -------
    Um dicionário com a mensagem
    """
    return {"message": "Bem-vindo à API de Livros 📚! Acesse a documentação interativa em /docs"}

@router.get("/api/v1/books", status_code=status.HTTP_200_OK)
async def list_books(db: db_dependency):
    """
    Lista todos os livros disponíveis na base de dados

    Returns
    -------
     Uma lista com todos os livros disponíveis
    """
    return db.query(Books).all()
    # return [book["title"] for book in df_books.to_dict(orient="records") if "title" in book]

@router.get("/api/v1/books/{book_id}")
async def get_book(db: db_dependency, book_id: int):
    """
    Retorna detalhes completos de um livro específico pelo ID

    Parameters
    ----------
    book_id : int
        Id do livro
    Raises
    ------
    HTTPException
        Se o id não encontrado na base de dados

    Returns
    -------
    Um dicionário contendo todas as informações do livro
    """
    id_book = db.query(Books).filter(Books.id == book_id).first()
    if id_book is not None:
        return id_book
    raise HTTPException(status_code=404, detail="Livro não encontrado")


@router.get("/api/v1/books/search")
async def search_books(
    db: db_dependency,
    title: Optional[str] = Query(None, description="Título parcial"),
    category: Optional[str] = Query(None, description="Categoria do livro"),
):
    """
        Pesquisa livros com base no título e/ou categoria.

    Este endpoint permite filtrar os livros disponíveis com base em uma correspondência parcial
    no título e/ou na categoria. A busca é case-insensitive.

    Parâmetros
    ----------
    title : Optional[str]
        Título parcial do livro a ser pesquisado. Se fornecido, o resultado incluirá
        apenas livros cujo título contenha esse valor.
    category : Optional[str]
        Categoria do livro a ser filtrada. Se fornecido, o resultado incluirá
        apenas livros dessa categoria.

    Retorno
    -------
    List[dict]
        Uma lista de dicionários representando os livros que correspondem aos critérios de busca.
        Cada dicionário contém os campos do DataFrame original.
    """
    query = db.query(Books)
    if title:
        query = query.filter(Books.title.ilike(f"%{title}%"))
    if category:
        query = query.filter(Books.category.ilike(f"%{category}%"))
    results = query.all()
    return [book.__dict__ for book in results]

@router.get("/api/v1/categories")
async def list_categories(db: db_dependency):
    """
    Lista todas as categorias de livros disponíveis

    Returns
    -------
    Uma lista contendo todas as categorias disponíveis
    """
    categories = db.query(Books.category).distinct().all()
    return [category[0] for category in categories]

@router.get("/api/v1/health")
async def health_check(db: db_dependency):
    """
    Verifica status da api e conectividade com os dados

    Returns
    ---------
    JSONResponse
        Um dicionário json com o status da api e mensagem
    """
    try:
        db.query(Books).first()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "API funcional e conectada ao bd"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Não foi possível conectar ao bd",
                "detail": str(e),
            },
        )