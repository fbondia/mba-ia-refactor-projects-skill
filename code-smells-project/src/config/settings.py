import os
from pathlib import Path


def load_settings():
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is required")

    origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    return {
        "SECRET_KEY": secret_key,
        "DEBUG": os.getenv("FLASK_DEBUG", "false").lower() == "true",
        "DATABASE_PATH": os.getenv(
            "DATABASE_PATH", str(Path(__file__).resolve().parents[2] / "loja.db")
        ),
        "ADMIN_TOKEN": os.getenv("ADMIN_TOKEN"),
        "CORS_ORIGINS": origins,
    }
