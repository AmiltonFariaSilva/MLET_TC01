import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{PROJECT_ROOT}/api_app.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://app_user:app_password@localhost:5432/app_db")
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {'check_same_thread': False} )
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False,
                                                    autoflush=False,bind = engine)
Base = declarative_base()


