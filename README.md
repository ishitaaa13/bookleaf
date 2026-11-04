# BookLeaf Author Support & Communication Portal — Starter

This repository starts the backend and data layer for the BookLeaf full-stack assignment.

## Included
- FastAPI backend
- SQLAlchemy models for authors, books, tickets, replies, and internal notes
- Seed script that imports the provided 10 authors and 18 books
- Idempotent seeding (rerunning updates matching IDs rather than duplicating them)
- SQLite local development setup, with PostgreSQL-ready `DATABASE_URL`
- Basic health, admin overview, and seed-verification endpoints

## Quick start
Follow `backend/README.md`.

## Planned next steps
1. Authentication and role-based access control.
2. Author book and ticket APIs.
3. Admin ticket queue, filters, assignment, status changes, replies, and notes.
4. AI classification, priority scoring, and response drafting.
5. React frontend, real-time/polling updates, tests, deployment, and complete documentation.


