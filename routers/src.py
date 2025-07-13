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
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Carregar os dados do CSV

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOKS_CSV_PATH =  PROJECT_ROOT/ "data" / "books.csv"

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
    return {"message": "Bem vindo , Acesse /docs para a documentação"}


@router.get("/api/v1/health")
async def health_check(db:db_dependency): 
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
            status_code = status.HTTP_200_OK, 
            content = {"status": "ok", "message": "API funcional e conectada ao bd"}
        )
    except Exception as e:
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content = {"status": "error", "message": "Não foi possível conectar ao bd", 
                       "detail":str(e)}
        )
            
        
@router.get("/api/v1/books", status_code = status.HTTP_200_OK)
async def list_books(db:db_dependency):
    """
    Lista todos os livros disponíveis na base de dados
    
    Returns
    -------
     Uma lista com todos os livros disponíveis
    """
    return db.query(Books).filter(Books.title).all()
    # return [book["title"] for book in df_books.to_dict(orient="records") if "title" in book]

@router.get("/api/v1/books/search")
async def search_books(
    db: db_dependency, 
    title: Optional[str] = Query(None, description="Título parcial"),
    category: Optional[str] = Query(None, description="Categoria do livro")
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

@router.get("/api/v1/books/top-rated")
async def list_titles_top_rated(db: db_dependency, limit: int = 10):
    """ 
    Retorna os títulos melhores rankeados
    
    Parameters
    ----------
    limit: int 
        Número máximo de livros a retornar (default = 10)
    
    Returns 
    -------
    Lista com os títulos dos livros mais bem avaliados 
    """
    # Supondo que o campo de ranking seja 'rating' (quanto maior, melhor)
    top_books = (
        db.query(Books)
        .order_by(Books.rating.desc())
        .limit(limit)
        .all()
    )
    return [book.title for book in top_books]

@router.get("/api/v1/books/price-range")
async def price_range(current_user: Annotated[dict, Depends(get_current_user)], 
                      db:db_dependency, min: float, max: float):
    """
    Retorna livros cujo preço está dentro de um intervalo
    
    Parameters
    ----------
    min: float 
        Preço mínimo
    max: float 
        Preço máximo
    Returns 
    -------
    Lista de livros com preços no intervalo [min, max]
    """
    filtered = (
        db.query(Books)
        .filter(Books.price >= min, Books.price <= max)
        .all()
    )
    return [book.title for book in filtered]

@router.get("/api/v1/stats/overview")
async def collection_statistics(db: db_dependency):
    """
    Retorna estatísticas gerais da coleção
    
    Returns
    -------
    dicionário com as estatísticas 
    """
    from sqlalchemy import func

    total_books = db.query(func.count(Books.id)).scalar()
    avg_price = db.query(func.avg(Books.price)).scalar()
    avg_price = round(avg_price, 2) if avg_price is not None else None

    # Get rating distribution
    rating_counts = (
        db.query(Books.rating, func.count(Books.rating))
        .group_by(Books.rating)
        .order_by(Books.rating)
        .all()
    )
    rating_distribution = {rating: count for rating, count in rating_counts}

    return {
        "total_livros": total_books,
        "preço_medio": avg_price,
        "distribuição_ratings": rating_distribution
    }

@router.get("/api/v1/stats/categories")
async def category_statistics(db: db_dependency):
    """
    Retorna estatísticas detalhadas por categoria 
    
    Returns
    -------
    dicionário com as estatísticas
    """
    from sqlalchemy import func

    results = (
        db.query(
            Books.category.label("category"),
            func.count(Books.title).label("total_livros"),
            func.avg(Books.price).label("preco_medio"),
            func.min(Books.price).label("preco_minimo"),
            func.max(Books.price).label("preco_maximo"),
        )
        .group_by(Books.category)
        .all()
    )

    return [
        {
            "category": row.category,
            "total_livros": row.total_livros,
            "preco_medio": round(row.preco_medio, 2) if row.preco_medio is not None else None,
            "preco_minimo": round(row.preco_minimo, 2) if row.preco_minimo is not None else None,
            "preco_maximo": round(row.preco_maximo, 2) if row.preco_maximo is not None else None,
        }
        for row in results
    ]

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
    

@router.get("/api/v1/categories")
async def list_categories(db:db_dependency):
    """
    Lista todas as categorias de livros disponíveis
    
    Returns 
    -------
    Uma lista contendo todas as categorias disponíveis
    """
    categories = db.query(Books.category).distinct().all()
    return [category[0] for category in categories]






