from sqlalchemy import Column, Integer, String, Float
from database import Base


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String)
    price = Column(Float)
    rating = Column(Integer)
    availability = Column(String)
    category = Column(String) 
    image_url = Column(String)