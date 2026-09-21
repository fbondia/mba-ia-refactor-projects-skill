import os
from pathlib import Path


def load_settings():
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is required")
    default_db = f"sqlite:///{Path(__file__).resolve().parents[1] / 'tasks.db'}"
    origins = [
        value.strip()
        for value in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if value.strip()
    ]
    return {
        "SECRET_KEY": secret_key,
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", default_db),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "TOKEN_MAX_AGE": int(os.getenv("TOKEN_MAX_AGE", "3600")),
        "CORS_ORIGINS": origins,
        "DEBUG": os.getenv("FLASK_DEBUG", "false").lower() == "true",
    }
