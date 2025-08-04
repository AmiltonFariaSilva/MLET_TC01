
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
import os
import models 
from routers import auth, src
from database import Base, engine

# Carrega variáveis de ambiente
#load_dotenv("C:/Users/anny/Documents/MLTE/credenciais.env")

app = FastAPI(
    title="BookScraper API",
    version="1.0.0",
    description="API para servir dados do Snowflake"
)


#Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(src.router)