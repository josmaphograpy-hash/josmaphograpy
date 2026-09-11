# josmaphograpy

Sitio del fotógrafo **Josman Sanchez Zabaleta** con arquitectura separada:

| Pieza | Dónde | Rol |
|-------|--------|-----|
| **Frontend** | Vercel (`/frontend`) | Sitio público |
| **Backend** | Render (`app.py`) | API + panel `/admin` |
| **Imágenes** | Cloudinary | Uploads del panel |
| **Base de datos** | TiDB Cloud | MySQL compatible |

Repo: https://github.com/josmaphograpy-hash/josmaphograpy

---

## Desarrollo local

```powershell
cd "D:\Pagina Josman"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python app.py
```

- Público (SSR Flask): http://127.0.0.1:5000/
- API: http://127.0.0.1:5000/api/public
- Admin: http://127.0.0.1:5000/admin (`josman` / `josman2024`)
- Front estático: abre `frontend/` con Live Server o `npx serve frontend`

Sin Cloudinary/TiDB, usa SQLite + carpeta `static/uploads`.

---

## Variables de entorno

Ver `.env.example`.

### Render (backend)
- `SECRET_KEY`
- `DATABASE_URL` (TiDB) **o** `TIDB_HOST`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_DATABASE`, `TIDB_PORT`
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- `FRONTEND_URL` (URL de Vercel)
- `CORS_ORIGINS`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`

Start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Vercel (frontend)
1. Root Directory: `frontend`
2. En `frontend/vercel.json` cambia el rewrite al host real de Render
3. Opcional: en `frontend/js/config.js` pon `window.API_BASE = "https://TU-API.onrender.com/api"`

### TiDB Cloud
1. Crea cluster Serverless
2. Crea base `josman`
3. Copia connection string → `DATABASE_URL` con prefijo `mysql+pymysql://`

### Cloudinary
1. Dashboard → API Keys
2. Carpeta sugerida: `josman`

---

## Panel admin (Render)

`https://TU-API.onrender.com/admin`

Gestiona fotos, planes, servicios, textos, redes y comentarios.
