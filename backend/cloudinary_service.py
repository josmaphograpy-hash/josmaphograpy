"""Subida de imágenes a Cloudinary (con fallback local en desarrollo)."""

from __future__ import annotations

import uuid
from pathlib import Path

import cloudinary
import cloudinary.uploader
from flask import current_app, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def configure_cloudinary() -> bool:
    name = current_app.config.get("CLOUDINARY_CLOUD_NAME")
    key = current_app.config.get("CLOUDINARY_API_KEY")
    secret = current_app.config.get("CLOUDINARY_API_SECRET")
    if not (name and key and secret):
        return False
    cloudinary.config(
        cloud_name=name,
        api_key=key,
        api_secret=secret,
        secure=True,
    )
    return True


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file_storage) -> str | None:
    """
    Sube a Cloudinary si hay credenciales.
    En local sin Cloudinary, guarda en static/uploads.
    Devuelve siempre una URL pública (https://...) o path relativo local.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    if configure_cloudinary():
        folder = current_app.config.get("CLOUDINARY_FOLDER", "josman")
        result = cloudinary.uploader.upload(
            file_storage,
            folder=folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        return result.get("secure_url") or result.get("url")

    # Fallback local (solo desarrollo)
    upload_dir = Path(current_app.root_path) / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(upload_dir / name)
    return f"uploads/{name}"


def public_image_url(path: str | None) -> str:
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return url_for("static", filename=path, _external=True)
