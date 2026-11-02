# BookLeaf backend starter

## Requirements
- Python 3.10+
- pip

## Setup (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/seed_data.py
uvicorn app.main:app --reload
```

Open:
- API health: http://127.0.0.1:8000/api/health
- Swagger docs: http://127.0.0.1:8000/docs
- Development seed verification: http://127.0.0.1:8000/api/authors

The database defaults to SQLite so the project runs locally without installing a database server. You can set `DATABASE_URL` to a PostgreSQL connection string later.

## Important
This is a foundation, not the finished assignment. The author listing and admin overview endpoints are intentionally for local development and are not yet protected by authentication. Do not deploy this starter publicly until authentication, authorization, validation, and production configuration are implemented.
