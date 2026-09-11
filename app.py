"""Backend Josman: API (Vercel front) + panel admin (Render)."""

from __future__ import annotations

import os
import uuid
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from api import api_bp
from cloudinary_service import public_image_url, save_upload
from config import Config
from models import (
    Admin,
    Package,
    Photo,
    Review,
    ServiceAddon,
    SiteSettings,
    SocialLink,
    db,
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(
    app,
    resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
    supports_credentials=False,
)
app.register_blueprint(api_bp)

login_manager = LoginManager(app)
login_manager.login_view = "admin_login"
login_manager.login_message = "Inicia sesión para acceder al panel."

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(Admin, int(user_id))


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        return view(*args, **kwargs)

    return wrapped


def get_settings() -> SiteSettings:
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    return settings


def seed_database() -> None:
    if not Admin.query.first():
        admin = Admin(username="josman")
        admin.set_password("josman2024")
        db.session.add(admin)

    if not SiteSettings.query.first():
        db.session.add(SiteSettings())

    if not SocialLink.query.first():
        defaults = [
            ("Instagram", "https://instagram.com", "fa-brands fa-instagram", 1),
            ("Pinterest", "https://pinterest.com", "fa-brands fa-pinterest-p", 2),
            ("Vimeo", "https://vimeo.com", "fa-brands fa-vimeo-v", 3),
        ]
        for platform, url, icon, order in defaults:
            db.session.add(
                SocialLink(platform=platform, url=url, icon=icon, sort_order=order)
            )

    if not Photo.query.first():
        samples = [
            (
                "El Ritual del Vestido",
                "Preparativos de la Novia",
                "Hotel Santa Clara · Cartagena",
                "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800&auto=format&fit=crop",
            ),
            (
                "Promesas Eternas",
                "Ceremonia al Atardecer",
                "Country Club · Barranquilla",
                "https://images.unsplash.com/photo-1529636798458-92182e662485?q=80&w=800&auto=format&fit=crop",
            ),
            (
                "Intimidad Dorada",
                "Retrato Editorial",
                "Playa Marina · Puerto Colombia",
                "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?q=80&w=800&auto=format&fit=crop",
            ),
            (
                "La Celebración del Amor",
                "Recepción & Fiesta",
                "Casa 1537 · Cartagena",
                "https://images.unsplash.com/photo-1544078751-58fee2d8a03b?q=80&w=800&auto=format&fit=crop",
            ),
            (
                "La Micro-Poesía",
                "Detalles Fine Art",
                "Estudio Privado · Barranquilla",
                "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?q=80&w=800&auto=format&fit=crop",
            ),
            (
                "Atardecer en la Ciénaga",
                "Sesión Save the Date",
                "Santa Marta Destino",
                "https://images.unsplash.com/photo-1583939003579-730e3918a45a?q=80&w=800&auto=format&fit=crop",
            ),
        ]
        for i, (title, category, location, url) in enumerate(samples):
            db.session.add(
                Photo(
                    title=title,
                    category=category,
                    location=location,
                    image_path=url,
                    sort_order=i,
                    is_published=True,
                )
            )

    if not Review.query.filter_by(is_approved=True).first():
        samples = [
            (
                "Mariana & Camilo",
                "Boda en Hotel Dan Carlton · Barranquilla",
                "Josman logró capturar momentos que ni siquiera sabíamos que habían sucedido. Al ver nuestro libro fotográfico volvimos a llorar de la emoción.",
                5,
            ),
            (
                "Valentina & Mateo",
                "Boda Destino · Cartagena de Indias",
                "La mejor decisión de nuestra boda destino en Cartagena. La calidad estética fine art es de otro nivel.",
                5,
            ),
            (
                "Isabella & Santiago",
                "Boda Campestre · Santa Marta",
                "El trabajo en película de 35mm le dio un toque poético inigualable a nuestra boda. Josman es un verdadero artista.",
                5,
            ),
        ]
        for name, event, comment, rating in samples:
            db.session.add(
                Review(
                    author_name=name,
                    event_info=event,
                    comment=comment,
                    rating=rating,
                    is_approved=True,
                )
            )

    if not Package.query.first():
        packages = [
            Package(
                key="pkg1",
                badge="Íntima & Elopement",
                name="Colección Íntima",
                short_desc="6 Horas de Cobertura · 1 Fotógrafo",
                description="Ideal para bodas exclusivas, elopements y civil de escala reducida.",
                features="\n".join(
                    [
                        "6 Horas de Cobertura Continua",
                        "1 Fotógrafo Principal (Josman Sanchez)",
                        "Galería Online Privada en Alta Resolución",
                        "+350 Fotografías Editadas Fine Art",
                        "Entrega en 25 Días Hábiles",
                    ]
                ),
                price=4500000,
                is_featured=False,
                sort_order=1,
            ),
            Package(
                key="pkg2",
                badge="Full Day Premium",
                name="Colección Esencial",
                short_desc="10 Horas · 2 Fotógrafos · Sesión Save The Date",
                description="Cobertura completa desde los preparativos hasta la fiesta principal.",
                features="\n".join(
                    [
                        "10 Horas de Cobertura Completa",
                        "2 Fotógrafos Profesionales (Equipo JSZ)",
                        "Sesión Save The Date de Regalo",
                        "Galería Online VIP con Descargas Ilimitadas",
                        "+650 Fotografías Editadas",
                        "Caja de Madera Custom con 25 Impresiones Fine Art",
                    ]
                ),
                price=7800000,
                is_featured=True,
                sort_order=2,
            ),
            Package(
                key="pkg3",
                badge="Experiencia VIP / Multi-Día",
                name="Gran Historia VIP",
                short_desc="Cobertura Ilimitada · Photobook Fine Art · Multi-Día",
                description="Para bodas destino y bodas de ultra-lujo sin restricciones de tiempo.",
                features="\n".join(
                    [
                        "Cobertura Ilimitada del Día de la Boda",
                        "Cobertura de Cóctel de Bienvenida (Día Anterior)",
                        "2 Fotógrafos Principales + Asistente",
                        "Photobook Artesanal en Lino Importado (30x30cm)",
                        "Cobertura Análoga en Película 35mm",
                        "Prioridad de Entrega Express (15 Días)",
                    ]
                ),
                price=12500000,
                is_featured=False,
                sort_order=3,
            ),
        ]
        db.session.add_all(packages)

    if not ServiceAddon.query.first():
        addons = [
            ServiceAddon(
                key="add1",
                name="Sesión Pre-Boda",
                description="Sesión romántica de 2 horas en exterior con concepto Save The Date.",
                icon="fa-solid fa-heart",
                price=1300000,
                sort_order=1,
            ),
            ServiceAddon(
                key="add2",
                name="Película Análoga 35mm",
                description="Captura estética vintage con rollo fotográfico real de colección.",
                icon="fa-solid fa-film",
                price=1700000,
                sort_order=2,
            ),
            ServiceAddon(
                key="add3",
                name="Photobook Fine Art",
                description="Libro impreso en lino o piel italiana con papel fotográfico de archivo.",
                icon="fa-solid fa-book-open",
                price=2200000,
                sort_order=3,
            ),
            ServiceAddon(
                key="add4",
                name="Video Teaser (Reels)",
                description="Highlight en formato vertical de 60s optimizado para redes sociales.",
                icon="fa-solid fa-clapperboard",
                price=1900000,
                sort_order=4,
            ),
        ]
        db.session.add_all(addons)

    db.session.commit()


def photo_src(path: str) -> str:
    return public_image_url(path)


app.jinja_env.globals["photo_src"] = photo_src


# ─── Sitio público ───────────────────────────────────────────────


@app.route("/")
def index():
    settings = get_settings()
    photos = (
        Photo.query.filter_by(is_published=True)
        .order_by(Photo.sort_order.asc(), Photo.created_at.desc())
        .all()
    )
    reviews = (
        Review.query.filter_by(is_approved=True)
        .order_by(Review.created_at.desc())
        .limit(12)
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
    avg_rating = (
        db.session.query(db.func.avg(Review.rating))
        .filter_by(is_approved=True)
        .scalar()
    )
    quote_packages = {
        p.key: {"name": p.name, "price": p.price, "short_desc": p.short_desc}
        for p in packages
    }
    quote_addons = {
        a.key: {"name": a.name, "price": a.price} for a in addons
    }
    featured_key = next((p.key for p in packages if p.is_featured), None)
    if not featured_key and packages:
        featured_key = packages[0].key

    return render_template(
        "index.html",
        settings=settings,
        photos=photos,
        reviews=reviews,
        socials=socials,
        packages=packages,
        addons=addons,
        quote_packages=quote_packages,
        quote_addons=quote_addons,
        featured_key=featured_key,
        avg_rating=round(avg_rating or 0, 1),
        review_count=Review.query.filter_by(is_approved=True).count(),
    )


@app.route("/comentario", methods=["POST"])
def submit_review():
    name = (request.form.get("author_name") or "").strip()
    email = (request.form.get("author_email") or "").strip()
    event_info = (request.form.get("event_info") or "").strip()
    comment = (request.form.get("comment") or "").strip()
    rating = request.form.get("rating", type=int) or 5
    photo_id = request.form.get("photo_id", type=int)

    if not name or not comment:
        flash("Nombre y comentario son obligatorios.", "error")
        return redirect(url_for("index") + "#opiniones")

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
    flash(
        "¡Gracias! Tu comentario fue enviado y se publicará cuando Josman lo apruebe.",
        "success",
    )
    return redirect(url_for("index") + "#opiniones")


# ─── Auth admin ──────────────────────────────────────────────────


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for("admin_dashboard"))
        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
@admin_required
def admin_logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("admin_login"))


# ─── Panel admin ─────────────────────────────────────────────────


@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        photo_count=Photo.query.count(),
        published_count=Photo.query.filter_by(is_published=True).count(),
        pending_reviews=Review.query.filter_by(is_approved=False).count(),
        approved_reviews=Review.query.filter_by(is_approved=True).count(),
        social_count=SocialLink.query.filter_by(is_active=True).count(),
        package_count=Package.query.filter_by(is_active=True).count(),
        addon_count=ServiceAddon.query.filter_by(is_active=True).count(),
        settings=get_settings(),
    )


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_required
def admin_settings():
    settings = get_settings()
    if request.method == "POST":
        settings.brand_name = request.form.get("brand_name", settings.brand_name).strip()
        settings.tagline = request.form.get("tagline", settings.tagline).strip()
        settings.hero_title = request.form.get("hero_title", settings.hero_title).strip()
        settings.hero_subtitle = request.form.get(
            "hero_subtitle", settings.hero_subtitle
        ).strip()
        settings.about_title = request.form.get("about_title", settings.about_title).strip()
        settings.about_text = request.form.get("about_text", settings.about_text).strip()
        settings.location = request.form.get("location", settings.location).strip()
        settings.whatsapp = request.form.get("whatsapp", settings.whatsapp).strip()
        settings.email = request.form.get("email", settings.email).strip()
        settings.currency = request.form.get("currency", settings.currency or "COP").strip()

        uploaded = save_upload(request.files.get("hero_image_file"))
        if uploaded:
            settings.hero_image = uploaded
        else:
            hero_url = (request.form.get("hero_image_url") or "").strip()
            if hero_url:
                settings.hero_image = hero_url

        db.session.commit()
        flash("Información del sitio actualizada.", "success")
        return redirect(url_for("admin_settings"))

    return render_template("admin/settings.html", settings=settings)


@app.route("/admin/photos")
@admin_required
def admin_photos():
    photos = Photo.query.order_by(Photo.sort_order.asc(), Photo.created_at.desc()).all()
    return render_template("admin/photos.html", photos=photos)


@app.route("/admin/photos/new", methods=["GET", "POST"])
@admin_required
def admin_photo_new():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            flash("El título es obligatorio.", "error")
            return redirect(url_for("admin_photo_new"))

        image_path = save_upload(request.files.get("image_file"))
        if not image_path:
            image_path = (request.form.get("image_url") or "").strip()
        if not image_path:
            flash("Sube una imagen o pega una URL.", "error")
            return redirect(url_for("admin_photo_new"))

        photo = Photo(
            title=title,
            category=(request.form.get("category") or "").strip(),
            location=(request.form.get("location") or "").strip(),
            description=(request.form.get("description") or "").strip(),
            image_path=image_path,
            is_published=bool(request.form.get("is_published")),
            sort_order=request.form.get("sort_order", type=int) or 0,
        )
        db.session.add(photo)
        db.session.commit()
        flash("Foto agregada a la galería.", "success")
        return redirect(url_for("admin_photos"))

    return render_template("admin/photo_form.html", photo=None)


@app.route("/admin/photos/<int:photo_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_photo_edit(photo_id: int):
    photo = db.session.get(Photo, photo_id) or abort(404)

    if request.method == "POST":
        photo.title = (request.form.get("title") or photo.title).strip()
        photo.category = (request.form.get("category") or "").strip()
        photo.location = (request.form.get("location") or "").strip()
        photo.description = (request.form.get("description") or "").strip()
        photo.is_published = bool(request.form.get("is_published"))
        photo.sort_order = request.form.get("sort_order", type=int) or 0

        uploaded = save_upload(request.files.get("image_file"))
        if uploaded:
            photo.image_path = uploaded
        else:
            image_url = (request.form.get("image_url") or "").strip()
            if image_url:
                photo.image_path = image_url

        db.session.commit()
        flash("Foto actualizada.", "success")
        return redirect(url_for("admin_photos"))

    return render_template("admin/photo_form.html", photo=photo)


@app.route("/admin/photos/<int:photo_id>/delete", methods=["POST"])
@admin_required
def admin_photo_delete(photo_id: int):
    photo = db.session.get(Photo, photo_id) or abort(404)
    if photo.image_path.startswith("uploads/"):
        local = UPLOAD_DIR / Path(photo.image_path).name
        if local.exists():
            local.unlink()
    db.session.delete(photo)
    db.session.commit()
    flash("Foto eliminada.", "success")
    return redirect(url_for("admin_photos"))


def _slugify_key(value: str, prefix: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or f"{prefix}{uuid.uuid4().hex[:6]}"


@app.route("/admin/packages")
@admin_required
def admin_packages():
    packages = Package.query.order_by(Package.sort_order.asc(), Package.id.asc()).all()
    return render_template("admin/packages.html", packages=packages)


@app.route("/admin/packages/new", methods=["GET", "POST"])
@admin_required
def admin_package_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("El nombre del plan es obligatorio.", "error")
            return redirect(url_for("admin_package_new"))

        key = (request.form.get("key") or "").strip() or _slugify_key(name, "pkg_")
        if Package.query.filter_by(key=key).first():
            key = f"{key}_{uuid.uuid4().hex[:4]}"

        package = Package(
            key=key,
            badge=(request.form.get("badge") or "").strip(),
            name=name,
            short_desc=(request.form.get("short_desc") or "").strip(),
            description=(request.form.get("description") or "").strip(),
            features=(request.form.get("features") or "").strip(),
            price=request.form.get("price", type=float) or 0,
            is_featured=bool(request.form.get("is_featured")),
            is_active=bool(request.form.get("is_active")),
            sort_order=request.form.get("sort_order", type=int) or 0,
        )
        db.session.add(package)
        db.session.commit()
        flash("Plan / colección creado.", "success")
        return redirect(url_for("admin_packages"))

    return render_template("admin/package_form.html", package=None)


@app.route("/admin/packages/<int:package_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_package_edit(package_id: int):
    package = db.session.get(Package, package_id) or abort(404)

    if request.method == "POST":
        package.badge = (request.form.get("badge") or "").strip()
        package.name = (request.form.get("name") or package.name).strip()
        package.short_desc = (request.form.get("short_desc") or "").strip()
        package.description = (request.form.get("description") or "").strip()
        package.features = (request.form.get("features") or "").strip()
        package.price = request.form.get("price", type=float) or 0
        package.is_featured = bool(request.form.get("is_featured"))
        package.is_active = bool(request.form.get("is_active"))
        package.sort_order = request.form.get("sort_order", type=int) or 0
        db.session.commit()
        flash("Plan actualizado.", "success")
        return redirect(url_for("admin_packages"))

    return render_template("admin/package_form.html", package=package)


@app.route("/admin/packages/<int:package_id>/delete", methods=["POST"])
@admin_required
def admin_package_delete(package_id: int):
    package = db.session.get(Package, package_id) or abort(404)
    db.session.delete(package)
    db.session.commit()
    flash("Plan eliminado.", "success")
    return redirect(url_for("admin_packages"))


@app.route("/admin/services")
@admin_required
def admin_services():
    services = ServiceAddon.query.order_by(
        ServiceAddon.sort_order.asc(), ServiceAddon.id.asc()
    ).all()
    return render_template("admin/services.html", services=services)


@app.route("/admin/services/new", methods=["GET", "POST"])
@admin_required
def admin_service_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("El nombre del servicio es obligatorio.", "error")
            return redirect(url_for("admin_service_new"))

        key = (request.form.get("key") or "").strip() or _slugify_key(name, "add_")
        if ServiceAddon.query.filter_by(key=key).first():
            key = f"{key}_{uuid.uuid4().hex[:4]}"

        service = ServiceAddon(
            key=key,
            name=name,
            description=(request.form.get("description") or "").strip(),
            icon=(request.form.get("icon") or "fa-solid fa-star").strip(),
            price=request.form.get("price", type=float) or 0,
            is_active=bool(request.form.get("is_active")),
            sort_order=request.form.get("sort_order", type=int) or 0,
        )
        db.session.add(service)
        db.session.commit()
        flash("Servicio adicional creado.", "success")
        return redirect(url_for("admin_services"))

    return render_template("admin/service_form.html", service=None)


@app.route("/admin/services/<int:service_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_service_edit(service_id: int):
    service = db.session.get(ServiceAddon, service_id) or abort(404)

    if request.method == "POST":
        service.name = (request.form.get("name") or service.name).strip()
        service.description = (request.form.get("description") or "").strip()
        service.icon = (request.form.get("icon") or service.icon).strip()
        service.price = request.form.get("price", type=float) or 0
        service.is_active = bool(request.form.get("is_active"))
        service.sort_order = request.form.get("sort_order", type=int) or 0
        db.session.commit()
        flash("Servicio actualizado.", "success")
        return redirect(url_for("admin_services"))

    return render_template("admin/service_form.html", service=service)


@app.route("/admin/services/<int:service_id>/delete", methods=["POST"])
@admin_required
def admin_service_delete(service_id: int):
    service = db.session.get(ServiceAddon, service_id) or abort(404)
    db.session.delete(service)
    db.session.commit()
    flash("Servicio eliminado.", "success")
    return redirect(url_for("admin_services"))


@app.route("/admin/social", methods=["GET", "POST"])
@admin_required
def admin_social():
    if request.method == "POST":
        platform = (request.form.get("platform") or "").strip()
        url = (request.form.get("url") or "").strip()
        icon = (request.form.get("icon") or "fa-solid fa-link").strip()
        if not platform or not url:
            flash("Plataforma y URL son obligatorios.", "error")
        else:
            db.session.add(
                SocialLink(
                    platform=platform,
                    url=url,
                    icon=icon,
                    sort_order=request.form.get("sort_order", type=int) or 0,
                    is_active=True,
                )
            )
            db.session.commit()
            flash("Red social agregada.", "success")
        return redirect(url_for("admin_social"))

    socials = SocialLink.query.order_by(SocialLink.sort_order.asc()).all()
    return render_template("admin/social.html", socials=socials)


@app.route("/admin/social/<int:link_id>/toggle", methods=["POST"])
@admin_required
def admin_social_toggle(link_id: int):
    link = db.session.get(SocialLink, link_id) or abort(404)
    link.is_active = not link.is_active
    db.session.commit()
    flash("Estado de la red actualizado.", "success")
    return redirect(url_for("admin_social"))


@app.route("/admin/social/<int:link_id>/delete", methods=["POST"])
@admin_required
def admin_social_delete(link_id: int):
    link = db.session.get(SocialLink, link_id) or abort(404)
    db.session.delete(link)
    db.session.commit()
    flash("Red social eliminada.", "success")
    return redirect(url_for("admin_social"))


@app.route("/admin/reviews")
@admin_required
def admin_reviews():
    pending = (
        Review.query.filter_by(is_approved=False)
        .order_by(Review.created_at.desc())
        .all()
    )
    approved = (
        Review.query.filter_by(is_approved=True)
        .order_by(Review.created_at.desc())
        .all()
    )
    return render_template(
        "admin/reviews.html", pending=pending, approved=approved
    )


@app.route("/admin/reviews/<int:review_id>/approve", methods=["POST"])
@admin_required
def admin_review_approve(review_id: int):
    review = db.session.get(Review, review_id) or abort(404)
    review.is_approved = True
    db.session.commit()
    flash("Comentario aprobado y visible en el sitio.", "success")
    return redirect(url_for("admin_reviews"))


@app.route("/admin/reviews/<int:review_id>/delete", methods=["POST"])
@admin_required
def admin_review_delete(review_id: int):
    review = db.session.get(Review, review_id) or abort(404)
    db.session.delete(review)
    db.session.commit()
    flash("Comentario eliminado.", "success")
    return redirect(url_for("admin_reviews"))


def ensure_schema() -> None:
    """Crea tablas y columnas faltantes (SQLite local y MySQL/TiDB en producción)."""
    db.create_all()
    from sqlalchemy import inspect as sa_inspect

    inspector = sa_inspect(db.engine)
    if "site_settings" not in inspector.get_table_names():
        return
    cols = {c["name"] for c in inspector.get_columns("site_settings")}
    if "currency" not in cols:
        with db.engine.begin() as conn:
            conn.execute(
                db.text(
                    "ALTER TABLE site_settings ADD COLUMN currency VARCHAR(10) DEFAULT 'COP'"
                )
            )


with app.app_context():
    ensure_schema()
    seed_database()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=port)
