# BookLeaf Author Support & Communication Portal

A full-stack web application that helps authors manage their books and communicate with the BookLeaf support team. Administrators can manage support tickets, assign requests, update ticket statuses, and communicate with authors.

## Features

### Author Portal
- Secure login and role-based access.
- View author profile and associated books.
- View and create support tickets.
- Select ticket categories and optionally associate a book with a request.
- View ticket replies and support updates.

### Admin Portal
- Admin dashboard with an overview of authors, books, and support tickets.
- View and manage support tickets.
- Assign tickets to support team members.
- Update ticket status and priority.
- Reply to author queries.
- Add and view internal notes.
- Access AI-assisted ticket support.

### Backend
- FastAPI REST API.
- SQLAlchemy database models.
- JWT-based authentication.
- Role-based access control.
- SQLite database for local development.
- Seed script for the provided sample authors and books.

### Frontend
- React application built with Vite.
- Separate author and admin dashboards.
- API integration with the FastAPI backend.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, CSS |
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT |
| API Documentation | Swagger UI |

## Project Structure

```text
bookleaf-portal-starter/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── config.py
│   ├── scripts/
│   │   └── seed_data.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── data/
│   └── bookleaf_sample_data.json
└── README.md
```

## Prerequisites

- Python 3.12 recommended
- Node.js and npm
- Git

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ishitaaa13/bookleaf.git
cd bookleaf
```

### 2. Backend setup

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the environment file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

### 3. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173/

### 4. Database and sample data

The application uses SQLite for local development. The supplied seed script is available at:

```text
backend/scripts/seed_data.py
```

Run the seed script using the instructions in `backend/README.md` if the database has not yet been populated.

## API Overview

| Area | Endpoint |
|---|---|
| Health | GET `/api/health` |
| Authentication | POST `/api/auth/login` |
| Current user | GET `/api/auth/me` |
| Admin overview | GET `/api/admin/overview` |
| Authors | GET `/api/authors` |
| Author books | GET `/api/author/books` |
| Author tickets | GET, POST `/api/author/tickets` |
| Admin tickets | GET `/api/admin/tickets` |
| Ticket assignment | PATCH `/api/admin/tickets/{ticket_id}/assign` |
| Ticket updates | PATCH `/api/admin/tickets/{ticket_id}/update` |
| Author replies | GET, POST `/api/author/tickets/{ticket_id}/replies` |
| Admin replies | POST `/api/admin/tickets/{ticket_id}/replies` |
| Internal notes | GET, POST `/api/admin/tickets/{ticket_id}/notes` |
| AI assistance | POST `/api/admin/tickets/{ticket_id}/ai-assist` |

## Verification

- Backend API endpoints tested through Swagger UI.
- Author and admin authentication tested.
- Ticket creation and management operations tested.
- Frontend production build verified using:

```bash
npm run build
```

## Security Notes

- This project is intended for local development and assignment evaluation.
- Keep environment variables and secrets in `.env`.
- Never commit `.env` or expose authentication secrets.
- Review security configuration and harden the application before public deployment.

## Application Screenshots

### Admin Dashboard

![Admin Frontend](docs/screenshots/admin.frontend.png)

![Admin Frontend - Additional View](docs/screenshots/admin.frontend2.png)

### Author Dashboard

![Author Frontend](docs/screenshots/author.frontend.png)

![Author Frontend - Additional View](docs/screenshots/author.frontend2.png)

### Backend API Documentation

![Backend API - Screenshot 1](docs/screenshots/backend1.png)

![Backend API - Screenshot 2](docs/screenshots/backend2.png)