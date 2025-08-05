from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Users(Base):
    """
    Criação de tabela users no db
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True,index = True)
    email= Column(String, unique = True)
    username = Column(String, unique = True)
    first_name = Column(String) 
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default = True)
    role = Column(String)
    
class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String)
    price = Column(Float)
    rating = Column(Integer)
    availability = Column(String)
    category = Column(String) 
    image_url = Column(String)