from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Books

router = APIRouter(
    prefix = '/ML', 
    tags = ['ML']
)

def convert_rating(rating_text):
    mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return mapping.get(rating_text, 0)

@router.get("/api/v1/ml/features")
def get_features(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    features = []
    for book in books:
        features.append({
            "title": book.title,
            "price": float(book.price.replace('£', '')),
            "rating": int(convert_rating(book.rating)),
            "availability": 1 if "In stock" in book.availability else 0,
            "category": book.category
        })
    return features

@router.get("/api/v1/ml/training-data")
def get_training_data(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    data = []
    for book in books:
        data.append({
            "title": book.title,
            "price": float(book.price.replace('£', '')),
            "rating": int(convert_rating(book.rating)),
            "availability": 1 if "In stock" in book.availability else 0,
            "category": book.category,
            "image_url": book.image_url
        })
    return data

class PredictionInput(BaseModel):
    price: float
    rating: int
    availability: int
    category: str

@router.post("/api/v1/ml/predictions")
def get_prediction(input_data: PredictionInput):
    score = 0.3 + 0.1 * input_data.rating + 0.05 * input_data.availability
    recommended = score > 0.7
    return {
        "recommended": recommended,
        "score": round(score, 2)
    }