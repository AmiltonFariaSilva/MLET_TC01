from fastapi import FastAPI
import models 
from routers import auth, src
from database import Base, engine

app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(src.router)


