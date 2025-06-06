from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pandas as pd

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
BOOKS_CSV_PATH = "data/books.csv"
try:
    df_books = pd.read_csv(BOOKS_CSV_PATH)
except Exception as e:
    print(f"Erro ao carregar o CSV: {e}")
    df_books = pd.DataFrame()

# Converte dataframe em dicionário com id como chave (opcional)
df_books.set_index("id", inplace=True)
books_dict = df_books.to_dict(orient="index")

# Endpoints obrigatórios

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/books")
def list_books():
    return list(books_dict.values())

@app.get("/api/v1/books/{book_id}")
def get_book(book_id: int):
    book = books_dict.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@app.get("/api/v1/books/search")
def search_books(
    title: Optional[str] = Query(None, description="Título parcial"),
    category: Optional[str] = Query(None, description="Categoria do livro")
):
    filtered = df_books
    if title:
        filtered = filtered[filtered["title"].str.contains(title, case=False, na=False)]
    if category:
        filtered = filtered[filtered["category"].str.contains(category, case=False, na=False)]
    return filtered.to_dict(orient="records")

@app.get("/api/v1/categories")
def list_categories():
    return sorted(df_books["category"].unique().tolist())
