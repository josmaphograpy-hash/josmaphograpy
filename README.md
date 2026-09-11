# josmaphograpy

Sitio web + panel del fotógrafo **Josman Sanchez Zabaleta**  
Repositorio: [josmaphograpy-hash/josmaphograpy](https://github.com/josmaphograpy-hash/josmaphograpy)

## Dos instancias

| URL | Quién | Para qué |
|-----|--------|----------|
| http://127.0.0.1:5000/ | Público | Galería, cotizador, comentarios y calificaciones |
| http://127.0.0.1:5000/admin | Fotógrafo | Fotos, planes, servicios, redes y moderación |

## Entorno virtual

```powershell
cd "D:\Pagina Josman"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Acceso admin

- Usuario: `josman`
- Contraseña: `josman2024`

(Cámbiala en producción.)

## Panel

1. **Fotos** — subir archivos o URL, editar y publicar
2. **Planes / Colecciones** — precios e inclusiones
3. **Servicios adicionales** — complementos del cotizador
4. **Información** — textos, WhatsApp, email y moneda
5. **Redes sociales** — Instagram, Facebook, TikTok, etc.
6. **Comentarios** — aprobar o eliminar opiniones (1–5 estrellas)
