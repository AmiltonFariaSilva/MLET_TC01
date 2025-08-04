import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from sqlalchemy import create_engine



# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# URL de conexão com o banco de dados
# No container, usamos o hostname do serviço docker-compose: "mlet_tc01_database"
user='amilton_faria',
password='Engenharia2025$'
account='ZAPPZJT-RCB40816'

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"ZAPPZJT-RCB40816.snowflakecomputing.com://{user}:{password}@{account}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
