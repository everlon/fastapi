from re import search
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pymongo import MongoClient
from datetime import datetime


DATABASE_URL = "sqlite:///./product.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MONGO_DB_URL = "mongodb://root:pwd@mongodb:27017"
MONGO_DB_URL = "mongodb://root:pwd@localhost:27017"
client = MongoClient(MONGO_DB_URL)
db = client["product_logs"]

# Registrar LOGS DE VISUALIZAÇÃO
async def log_product_view(product_id: int, search: dict = None):
    db.views.insert_one({
        "product_id": product_id,
        "viewed_at": datetime.utcnow(),
        "search": search if search else {}
    })

# Contar LOGS DE VISUALIZAÇÃO
async def get_product_views(id: int) -> list:
    # return db.views.count_documents({"product_id": id})

    views_cursor = db.views.find(
        {"product_id": id}, {"_id": 0, "product_id": 1, "viewed_at": 1, "search": 1})

    views = []
    for view in views_cursor:
        views.append({
            # "product_id": view["product_id"],
            "viewed_at": view["viewed_at"],
            "search": view.get("search", {})
        })

    return views
