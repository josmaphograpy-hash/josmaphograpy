"""Configuración del backend (Render + TiDB + Cloudinary)."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


def _database_uri() -> str:
    """
    Prioridad:
    1) DATABASE_URL (Render / TiDB Cloud)
    2) TIDB_* partes sueltas
    3) SQLite local para desarrollo
    """
    url = (os.environ.get("DATABASE_URL") or "").strip()
    if url:
        # Render a veces entrega postgres://; TiDB usa mysql
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    host = os.environ.get("TIDB_HOST")
    if host:
        user = os.environ.get("TIDB_USER", "root")
        password = os.environ.get("TIDB_PASSWORD", "")
        port = os.environ.get("TIDB_PORT", "4000")
        database = os.environ.get("TIDB_DATABASE", "josman")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_ca=&ssl_verify_cert=false"

    return f"sqlite:///{BASE_DIR / 'josman.db'}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(24)
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # CORS / frontend
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5500").rstrip("/")
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS",
            f"{FRONTEND_URL},http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:3000,http://localhost:3000",
        ).split(",")
        if o.strip()
    ]

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_FOLDER = os.environ.get("CLOUDINARY_FOLDER", "josman")

    # Admin seed
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "josman")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "josman2024")
