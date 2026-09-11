"""Configuración para local, Render, TiDB y Cloudinary."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def database_uri() -> str:
    """
    Prioridad:
    1) DATABASE_URL (TiDB Cloud / Render)
    2) TIDB_* por partes
    3) SQLite local
    """
    url = (os.environ.get("DATABASE_URL") or "").strip()
    if url:
        if url.startswith("mysql://"):
            url = "mysql+pymysql://" + url[len("mysql://") :]
        return url

    host = (os.environ.get("TIDB_HOST") or "").strip()
    if host:
        user = os.environ.get("TIDB_USER", "root")
        password = os.environ.get("TIDB_PASSWORD", "")
        port = os.environ.get("TIDB_PORT", "4000")
        database = os.environ.get("TIDB_DATABASE", "josman")
        # TiDB Cloud exige TLS; PyMySQL acepta ssl={"ssl": True}
        return (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            "?charset=utf8mb4"
        )

    return f"sqlite:///{BASE_DIR / 'josman.db'}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(24)
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 10,
    }
    # SSL para TiDB Cloud cuando hay host remoto
    if os.environ.get("TIDB_HOST") or (
        os.environ.get("DATABASE_URL", "").startswith(("mysql", "mysql+pymysql"))
    ):
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": {"ssl": True}}

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    FRONTEND_URL = (os.environ.get("FRONTEND_URL") or "http://127.0.0.1:5500").rstrip("/")
    _cors_raw = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS",
            f"{FRONTEND_URL},http://127.0.0.1:5500,http://localhost:5500,"
            "http://127.0.0.1:3000,http://localhost:3000",
        ).split(",")
        if o.strip()
    ]
    # Incluye cualquier preview/producción de Vercel
    CORS_ORIGINS = _cors_raw + [r"https://.*\.vercel\.app"]

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_FOLDER = os.environ.get("CLOUDINARY_FOLDER", "josman")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "josman")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "josman2024")
