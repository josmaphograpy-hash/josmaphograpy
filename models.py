"""Modelos de base de datos para el sitio del fotógrafo."""

from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class SiteSettings(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(120), default="Josman Sanchez")
    tagline = db.Column(db.String(200), default="Fine Art Wedding Photographer")
    hero_title = db.Column(db.String(300), default="Eternizando la poesía natural de tu boda.")
    hero_subtitle = db.Column(
        db.Text,
        default=(
            "Fotografía Fine Art & Documental por Josman Sanchez Zabaleta. "
            "Basado en Barranquilla. Capturo la esencia genuina, la luz cálida "
            "del Caribe y las emociones espontáneas sin posados forzados."
        ),
    )
    about_title = db.Column(
        db.String(300),
        default="Sin posados rígidos. Solo la verdad de tu historia.",
    )
    about_text = db.Column(
        db.Text,
        default=(
            "Hola, soy Josman Sanchez Zabaleta. Mi visión como fotógrafo se "
            "aleja de la dirección artificiosa. Creo firmemente que las "
            "fotografías más poderosas son aquellas que capturan la risa "
            "nerviosa antes de caminar hacia el altar."
        ),
    )
    location = db.Column(db.String(200), default="Barranquilla, Colombia")
    whatsapp = db.Column(db.String(40), default="573003017628")
    email = db.Column(db.String(120), default="contacto@josmansanchez.com")
    hero_image = db.Column(db.String(500), default="")
    currency = db.Column(db.String(10), default="COP")


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(120), default="")
    location = db.Column(db.String(200), default="")
    description = db.Column(db.Text, default="")
    image_path = db.Column(db.String(500), nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("Review", backref="photo", lazy=True, cascade="all, delete-orphan")


class SocialLink(db.Model):
    __tablename__ = "social_links"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(80), default="fa-solid fa-link")
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120), nullable=False)
    author_email = db.Column(db.String(120), default="")
    event_info = db.Column(db.String(200), default="")
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    is_approved = db.Column(db.Boolean, default=False)
    photo_id = db.Column(db.Integer, db.ForeignKey("photos.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Package(db.Model):
    """Colecciones / planes principales."""

    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    badge = db.Column(db.String(120), default="")
    name = db.Column(db.String(200), nullable=False)
    short_desc = db.Column(db.String(300), default="")
    description = db.Column(db.Text, default="")
    features = db.Column(db.Text, default="")  # una por línea
    price = db.Column(db.Float, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    @property
    def features_list(self):
        return [line.strip() for line in (self.features or "").splitlines() if line.strip()]


class ServiceAddon(db.Model):
    """Servicios / experiencias adicionales."""

    __tablename__ = "service_addons"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    icon = db.Column(db.String(80), default="fa-solid fa-star")
    price = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
