import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# URL de conexão com o banco de dados
# No container, usamos o hostname do serviço docker-compose: "mlet_tc01_database"
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://app_user:app_password@mlet_tc01_database:5432/app_db"
)

# Criação do engine e sessão
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
