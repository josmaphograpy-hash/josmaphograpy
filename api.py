"""API JSON para el frontend en Vercel."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from cloudinary_service import public_image_url
from models import Package, Photo, Review, ServiceAddon, SiteSettings, SocialLink, db

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _settings_payload(settings: SiteSettings) -> dict:
    return {
        "brand_name": settings.brand_name,
        "tagline": settings.tagline,
        "hero_title": settings.hero_title,
        "hero_subtitle": settings.hero_subtitle,
        "about_title": settings.about_title,
        "about_text": settings.about_text,
        "location": settings.location,
        "whatsapp": settings.whatsapp,
        "email": settings.email,
        "hero_image": public_image_url(settings.hero_image),
        "currency": settings.currency or "COP",
    }


@api_bp.get("/health")
def health():
    cloudinary_ready = bool(
        (current_app.config.get("CLOUDINARY_CLOUD_NAME") or "").strip()
        and (current_app.config.get("CLOUDINARY_API_KEY") or "").strip()
        and (current_app.config.get("CLOUDINARY_API_SECRET") or "").strip()
    )
    return jsonify(
        {
            "ok": True,
            "service": "josmaphograpy-api",
            "cloudinary": cloudinary_ready,
        }
    )


@api_bp.get("/public")
def public_site():
    """Todo lo que necesita el sitio público en una sola llamada."""
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()

    photos = (
        Photo.query.filter_by(is_published=True)
        .order_by(Photo.sort_order.asc(), Photo.created_at.desc())
        .all()
    )
    reviews = (
        Review.query.filter_by(is_approved=True)
        .order_by(Review.created_at.desc())
        .limit(24)
        .all()
    )
    socials = (
        SocialLink.query.filter_by(is_active=True)
        .order_by(SocialLink.sort_order.asc())
        .all()
    )
    packages = (
        Package.query.filter_by(is_active=True)
        .order_by(Package.sort_order.asc(), Package.id.asc())
        .all()
    )
    addons = (
        ServiceAddon.query.filter_by(is_active=True)
        .order_by(ServiceAddon.sort_order.asc(), ServiceAddon.id.asc())
        .all()
    )
    avg = (
        db.session.query(db.func.avg(Review.rating))
        .filter_by(is_approved=True)
        .scalar()
    )
    count = Review.query.filter_by(is_approved=True).count()
    featured = next((p.key for p in packages if p.is_featured), None)
    if not featured and packages:
        featured = packages[0].key

    return jsonify(
        {
            "settings": _settings_payload(settings),
            "photos": [
                {
                    "id": p.id,
                    "title": p.title,
                    "category": p.category,
                    "location": p.location,
                    "description": p.description,
                    "image_url": public_image_url(p.image_path),
                }
                for p in photos
            ],
            "reviews": [
                {
                    "id": r.id,
                    "author_name": r.author_name,
                    "event_info": r.event_info,
                    "comment": r.comment,
                    "rating": r.rating,
                }
                for r in reviews
            ],
            "socials": [
                {
                    "id": s.id,
                    "platform": s.platform,
                    "url": s.url,
                    "icon": s.icon,
                }
                for s in socials
            ],
            "packages": [
                {
                    "id": p.id,
                    "key": p.key,
                    "badge": p.badge,
                    "name": p.name,
                    "short_desc": p.short_desc,
                    "description": p.description,
                    "features": p.features_list,
                    "price": p.price,
                    "is_featured": p.is_featured,
                }
                for p in packages
            ],
            "addons": [
                {
                    "id": a.id,
                    "key": a.key,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "price": a.price,
                }
                for a in addons
            ],
            "featured_key": featured,
            "avg_rating": round(float(avg or 0), 1),
            "review_count": count,
            "api_base": request.url_root.rstrip("/"),
        }
    )


@api_bp.post("/reviews")
def create_review():
    data = request.get_json(silent=True) or request.form
    name = (data.get("author_name") or "").strip()
    email = (data.get("author_email") or "").strip()
    event_info = (data.get("event_info") or "").strip()
    comment = (data.get("comment") or "").strip()
    try:
        rating = int(data.get("rating") or 5)
    except (TypeError, ValueError):
        rating = 5
    photo_id = data.get("photo_id")
    try:
        photo_id = int(photo_id) if photo_id else None
    except (TypeError, ValueError):
        photo_id = None

    if not name or not comment:
        return jsonify({"ok": False, "error": "Nombre y comentario son obligatorios."}), 400

    rating = max(1, min(5, rating))
    if photo_id and not db.session.get(Photo, photo_id):
        photo_id = None

    review = Review(
        author_name=name[:120],
        author_email=email[:120],
        event_info=event_info[:200],
        comment=comment[:2000],
        rating=rating,
        photo_id=photo_id,
        is_approved=False,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(
        {
            "ok": True,
            "message": "Gracias. Tu comentario se publicará cuando el fotógrafo lo apruebe.",
        }
    ), 201
