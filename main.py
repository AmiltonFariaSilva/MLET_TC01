
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import models 
from routers import auth, src
from database import Base, engine

# Carrega variáveis de ambiente
load_dotenv("C:/Users/anny/Documents/MLTE/credenciais.env")

app = FastAPI(
    title="BookScraper API",
    version="1.0.0",
    description="API para servir dados do Snowflake"
)


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(src.router)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_engine():
    return create_engine(
        "snowflake://{user}:{pwd}@{acct}/{db}/{schema}?warehouse={wh}&role={role}".format(
            user=os.getenv("SNOWFLAKE_USER"),
            pwd=os.getenv("SNOWFLAKE_PWD"),
            acct=os.getenv("SNOWFLAKE_ACCT"),
            db=os.getenv("SNOWFLAKE_DB"),        
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            wh=os.getenv("SNOWFLAKE_WH"),        
            role=os.getenv("SNOWFLAKE_ROLE")     
        )
    )

try:
    engine = get_engine()
    QUERY = text("""
        SELECT id, title, category, price, rating 
        FROM DB_SCRAPE.SC_SCRAPE.TB_BOOKS_TO_SCRAPE  -- Nomes corrigidos
    """)
    df_books = pd.read_sql(QUERY, engine)
    df_books.set_index("id", inplace=True)
    books_dict = df_books.to_dict(orient="index")
except Exception as e:
    print(f"Erro crítico ao conectar ao Snowflake: {e}")
    raise SystemExit("Falha na inicialização: Verifique as credenciais e conexão")

@app.get("/")
async def root():
    return {"message": "Bem-vindo! Acesse /docs para a documentação"}

@app.get("/api/v1/health")
async def health_check():
    """
    Verifica status da API e conectividade com os dados.
    
    Returns
    -------
    JSONResponse
        Um dicionário JSON com o status da API e uma mensagem.
    """

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return JSONResponse(
            content={"status_code": status.HTTP_200_OK, "message": "API funcional"}
        )
    except Exception as e:
        return JSONResponse(
            content={"status_code": status.HTTP_503_SERVICE_UNAVAILABLE, "message": f"Erro no Snowflake: {str(e)}"}
        )

@app.get("/api/v1/books")
async def list_books():
    """
    Lista todos os livros disponíveis na base de dados
    
    Returns
    -------
     Uma lista com todos os livros disponíveis
    """
    return [book["title"] for book in df_books.to_dict(orient="records")]

@app.get("/api/v1/books/search")
async def search_books(
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
    filtered = df_books
    if title:
        filtered = filtered[filtered["title"].str.contains(title, case=False, na=False)]
    if category:
        filtered = filtered[filtered["category"].str.contains(category, case=False, na=False)]
    return filtered.to_dict(orient="records")

@app.get("/api/v1/books/top-rated")
async def list_titles_top_rated(limit: int = 10):
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
    top_books = df_books.sort_values(by="rating", ascending=False).head(limit)
    return top_books["title"].tolist()

@app.get("/api/v1/books/price-range")
async def price_range(min: float, max: float):
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
    filtered = df_books[(df_books["price"] >= min) & (df_books["price"] <= max)]
    return filtered["title"].tolist()

@app.get("/api/v1/stats/overview")
async def collection_statistics():
    """
    Retorna estatísticas gerais da coleção
    
    Returns
    -------
    dicionário com as estatísticas 
    """
    return {
        "total_livros": len(df_books),
        "preço_medio": round(df_books["price"].mean(), 2),
        "distribuição_ratings": df_books["rating"].value_counts().sort_index().to_dict()
    }

@app.get("/api/v1/stats/categories")
async def category_statistics(): 
    """
    Retorna estatísticas detalhadas por categoria 
    
    Returns
    -------
    dicionário com as estatísticas
    """
    grouped = df_books.groupby("category").agg(
        total_livros=("title", "count"),
        preco_medio=("price", "mean"),
        preco_minimo=("price", "min"),
        preco_maximo=("price", "max")
    ).round(2)
    return grouped.reset_index().to_dict(orient="records")

@app.get("/api/v1/books/{book_id}")
async def get_book(book_id: int):
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
    book = books_dict.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@app.get("/api/v1/categories")
async def list_categories():
    """
    Lista todas as categorias de livros disponíveis
    
    Returns 
    -------
    Uma lista contendo todas as categorias disponíveis
    """
    return sorted(df_books["category"].unique().tolist())

