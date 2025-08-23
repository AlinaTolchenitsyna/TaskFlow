import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    
    # SQLite база, файл в папке проекта
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'taskflow.db'}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
