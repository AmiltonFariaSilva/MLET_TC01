
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
import os
import models as models 
from routers import auth, src, ml, optional
from database import Base, engine

app = FastAPI(
    title="BookScraper API",
    version="1.0.0",
    description="API para servir dados do Snowflake"
)

app.include_router(auth.router)
app.include_router(src.router)
app.include_router(optional.router)
app.include_router(ml.router)