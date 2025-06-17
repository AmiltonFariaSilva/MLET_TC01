from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Optional
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="BookScraper API",
    version="1.0.0",
    description="API para servir dados raspados do site Books to Scrape"
)

# CORS Middleware (opcional para consumo externo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregar os dados do CSV

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOKS_CSV_PATH =  PROJECT_ROOT/ "data" / "books.csv"

try:
    df_books = pd.read_csv(BOOKS_CSV_PATH)
    df_books.set_index("id", inplace=True)
    books_dict = df_books.to_dict(orient="index")
     
except Exception as e:
    print(f"Erro ao carregar o CSV: {e}")
    df_books = pd.DataFrame()
    books_dict = {}


# Endpoints obrigatórios

@app.get("/")
async def root(): 
    """
    Mensagem inicial da api 
    
    Returns 
    -------
    Um dicionário com a mensagem 
    """
    return {"message": "Bem vindo , Acesse /docs para a documentação"}


@app.get("/api/v1/health")
async def health_check(): 
    """
    Verifica status da api e conectividade com os dados 
    
    Returns
    ---------
    JSONResponse 
        Um dicionário json com o status da api e mensagem
    """
    try: 
        if not BOOKS_CSV_PATH.exists():
            return JSONResponse(
                content = {"status_code":status.HTTP_503_SERVICE_UNAVAILABLE, "message": "Arquivo 'books.csv' não encontrado"}
            )
        return JSONResponse(
            content = {"status_code": status.HTTP_200_OK, "message": "API funcional"}
        )
    except Exception as e:
        return JSONResponse(
            content = {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}
        )
            
        
@app.get("/api/v1/books")
async def list_books():
    """
    Lista todos os livros disponíveis na base de dados
    
    Returns
    -------
     Uma lista com todos os livros disponíveis
    """
    return [book["title"] for book in df_books.to_dict(orient="records") if "title" in book]

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
    
    top_books = df_books.sort_values(by="rating", ascending = False).head(limit)
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
    filtered = df_books[(df_books["price"]>= min) & (df_books["price"]<=max)]
    return filtered["title"].tolist()

@app.get("/api/v1/stats/overview")
async def collection_statistics():
    """
    Retorna estatísticas gerais da coleção
    
    Returns
    -------
    dicionário com as estatísticas 
    """
    total_books = len(df_books)
    avg_price = round(df_books["price"].mean(), 2)
    rating_distribution = df_books["rating"].value_counts().sort_index().to_dict()
    
    return {
        "total_livros": total_books, 
        "preço_medio": avg_price, 
        "distribuição_ratings": rating_distribution
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


