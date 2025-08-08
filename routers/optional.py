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
    prefix="/api/v1/optional",
    tags=["OPT"]
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
        "distribuição_ratings": rating_distribution,
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
            "preco_medio": (
                round(row.preco_medio, 2) if row.preco_medio is not None else None
            ),
            "preco_minimo": (
                round(row.preco_minimo, 2) if row.preco_minimo is not None else None
            ),
            "preco_maximo": (
                round(row.preco_maximo, 2) if row.preco_maximo is not None else None
            ),
        }
        for row in results
    ]

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
    top_books = db.query(Books).order_by(Books.rating.desc()).limit(limit).all()
    return [book.title for book in top_books]


@router.get("/api/v1/books/price-range")
async def price_range(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: db_dependency,
    min: float,
    max: float,
):
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
    filtered = db.query(Books).filter(Books.price >= min, Books.price <= max).all()
    return [book.title for book in filtered]


