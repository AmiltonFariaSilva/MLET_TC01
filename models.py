from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP
from sqlalchemy.sql import text
from database import Base

class Users(Base):
    """
    Criação de tabela users no db
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    email = Column(String)
    username = Column(String)
    first_name = Column(String) 
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')
    
class Books(Base):
    __tablename__ = 'tb_books_to_scrape'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    rating = Column(Integer)
    availability = Column(String)
    category = Column(String) 
    image_url = Column(String)
    metadata_filename = Column(String)
    load_timestamp = Column(TIMESTAMP)