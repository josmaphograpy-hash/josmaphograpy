"""Subida de imágenes a Cloudinary (fallback local solo en desarrollo)."""

from __future__ import annotations

import os
import uuid
from io import BytesIO
from pathlib import Path

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import current_app, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


class UploadError(Exception):
    """Error controlado al subir una imagen."""


def configure_cloudinary() -> bool:
    """Configura el SDK. Acepta vars sueltas o CLOUDINARY_URL."""
    url = (os.environ.get("CLOUDINARY_URL") or "").strip()
    if url:
        # cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        cloudinary.config(cloudinary_url=url, secure=True)
        return True

    name = (current_app.config.get("CLOUDINARY_CLOUD_NAME") or "").strip()
    key = (current_app.config.get("CLOUDINARY_API_KEY") or "").strip()
    secret = (current_app.config.get("CLOUDINARY_API_SECRET") or "").strip()
    if not (name and key and secret):
        return False
    cloudinary.config(
        cloud_name=name,
        api_key=key,
        api_secret=secret,
        secure=True,
    )
    return True


def cloudinary_status() -> dict:
    """Diagnóstico seguro (sin secretos) para /api/health o admin."""
    configured = configure_cloudinary()
    if not configured:
        return {
            "configured": False,
            "ok": False,
            "error": "Faltan CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET (o CLOUDINARY_URL)",
        }
    try:
        cloudinary.api.ping()
        return {
            "configured": True,
            "ok": True,
            "cloud_name": cloudinary.config().cloud_name,
        }
    except Exception as exc:
        return {
            "configured": True,
            "ok": False,
            "cloud_name": cloudinary.config().cloud_name,
            "error": str(exc),
        }


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _is_production() -> bool:
    return bool(
        os.environ.get("RENDER")
        or os.environ.get("RENDER_SERVICE_ID")
        or current_app.config.get("ENV") == "production"
    )


def save_upload(file_storage) -> str | None:
    """Devuelve URL https (Cloudinary) o path relativo local (solo desarrollo).

    Lanza UploadError con mensaje claro si Cloudinary rechaza la subida.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise UploadError(
            f"Formato no permitido ({file_storage.filename}). Usa JPG, PNG, WEBP o GIF."
        )

    if configure_cloudinary():
        folder = (current_app.config.get("CLOUDINARY_FOLDER") or "josman").strip() or "josman"
        try:
            try:
                file_storage.stream.seek(0)
            except Exception:
                pass
            raw = file_storage.read()
            if not raw:
                raise UploadError("El archivo llegó vacío. Prueba otra imagen.")

            result = cloudinary.uploader.upload(
                BytesIO(raw),
                folder=folder,
                resource_type="image",
                use_filename=True,
                unique_filename=True,
                overwrite=False,
                filename_override=secure_filename(file_storage.filename) or "upload.jpg",
            )
            url = result.get("secure_url") or result.get("url")
            if not url:
                raise UploadError("Cloudinary no devolvió URL de la imagen.")
            return url
        except UploadError:
            raise
        except Exception as exc:
            current_app.logger.exception("Fallo subiendo a Cloudinary: %s", exc)
            msg = str(exc).strip() or "error desconocido"
            # Mensajes típicos más humanos
            low = msg.lower()
            if "invalid signature" in low or "signature" in low:
                hint = " (API_SECRET incorrecto o con espacios de más)"
            elif "unknown api key" in low or "invalid api key" in low:
                hint = " (API_KEY incorrecta)"
            elif "cloud_name" in low or "not found" in low:
                hint = " (CLOUD_NAME incorrecto)"
            else:
                hint = ""
            raise UploadError(f"Cloudinary rechazó la subida: {msg}{hint}") from exc

    if _is_production():
        raise UploadError(
            "Cloudinary no está configurado en Render. "
            "Define CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET."
        )

    upload_dir = Path(current_app.root_path) / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.stream.seek(0)
    file_storage.save(upload_dir / name)
    return f"uploads/{name}"


def public_image_url(path: str | None) -> str:
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return url_for("static", filename=path, _external=True)
