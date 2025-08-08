from typing import List, Optional
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import get_db
from models import Books

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["ML"]
)

def parse_price(value) -> Optional[float]:
    """Converte '£53.74', '  £ 53.74 ', 53.74, None -> float ou None
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace("\xa0", " ")
        
        s = s.replace("£", "").replace("R$", "").replace(",", "")
                
        m = re.search(r"(\d+(\.\d+)?)", s)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
        try:
            return float(s)
        except ValueError:
            return None
    return None

def convert_rating(rating_text) -> int:
    if rating_text is None:
        return 0
    if isinstance(rating_text, int):
        return max(0, min(5, rating_text))
    mapping = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
    }
    return mapping.get(str(rating_text), 0)

def to_availability_flag(text) -> int:
    if not text:
        return 0
    return 1 if "in stock" in text.lower() else 0

class FeatureOut(BaseModel):
    title: str
    price: Optional[float] = Field(default=None, description="Preço numérico")
    rating: int
    availability: int
    category: Optional[str] = None

class TrainingOut(FeatureOut):
    image_url: Optional[str] = None

class PredictionInput(BaseModel):
    price: float
    rating: int
    availability: int
    category: str

class PredictionOut(BaseModel):
    recommended: bool
    score: float

@router.get("/features", response_model=List[FeatureOut])
def get_features(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    features: List[FeatureOut] = []
    for book in books:
        features.append(FeatureOut(
            title=book.title,
            price=parse_price(book.price),
            rating=convert_rating(book.rating),
            availability=to_availability_flag(book.availability),
            category=book.category
        ))
    return features

@router.get("/training-data", response_model=List[TrainingOut])
def get_training_data(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    data: List[TrainingOut] = []
    for book in books:
        data.append(TrainingOut(
            title=book.title,
            price=parse_price(book.price),
            rating=convert_rating(book.rating),
            availability=to_availability_flag(book.availability),
            category=book.category,
            image_url=book.image_url
        ))
    return data

@router.post("/predictions", response_model=PredictionOut)
def get_prediction(input_data: PredictionInput):
    # Heurística simples (placeholder até ter modelo real)
    score = 0.30 + 0.10 * input_data.rating + 0.05 * input_data.availability
    recommended = score > 0.70
    return PredictionOut(
        recommended=recommended,
        score=round(float(score), 2)
    )
