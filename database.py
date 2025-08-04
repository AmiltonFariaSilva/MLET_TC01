import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from sqlalchemy import create_engine



# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# URL de conexão com o banco de dados
# No container, usamos o hostname do serviço docker-compose: "mlet_tc01_database"
user = "amilton_faria"
password = "Engenharia2025$"
account = "zappzjt-rcb40816"
database = "DB_SCRAPE"     # substitua pelo nome real
schema = "SC_SCRAPE"         # ou o schema que você usa
warehouse = "COMPUTE_WH"  # ou outro warehouse
role = "ROLE_BOOKS_SCRAPE"     # opcional, mas pode ser importante

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
