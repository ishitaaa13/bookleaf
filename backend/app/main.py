import json
import os
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.auth import (
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
)
from app.database import Base, engine, get_db
from app.models import (
    Author,
    Book,
    Ticket,
    TicketReply,
    InternalNote,
    UserAccount,
)
app = FastAPI(title="BookLeaf Author Support Portal")
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Other existing imports remain unchanged

app = FastAPI(title="BookLeaf Author Support Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketCreateRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=10000)
    category: Literal[
        "Royalty & Payments",
        "ISBN & Metadata Issues",
        "Printing & Quality",
        "Distribution & Availability",
        "Book Status & Production Updates",
        "General Inquiry",
    ] = "General Inquiry"
    book_id: str | None = None

class TicketAssignmentRequest(BaseModel):
    assigned_to: str = Field(min_length=3, max_length=255)
class TicketUpdateRequest(BaseModel):
    status: Literal["Open", "In Progress", "Resolved", "Closed"] | None = None
    priority: Literal["Low", "Medium", "High", "Urgent"] | None = None
class TicketReplyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class InternalNoteRequest(BaseModel):
    note: str = Field(min_length=1, max_length=10000)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health():
    return {"status": "ok"}
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#@app.post("/api/auth/login")
@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(UserAccount).where(UserAccount.email == payload.email)
    )

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is inactive",
        )

    return {
    "access_token": create_access_token(user),
    "token_type": "bearer",
    "role": user.role,
    "user": {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "author_id": user.author_id,
    },
    "expires_in": 1800,
}

    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800,
        "role": user.role,
    }    


@app.get("/api/admin/overview")
def admin_overview(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    return {
        "authors": db.scalar(select(func.count()).select_from(Author)) or 0,
        "books": db.scalar(select(func.count()).select_from(Book)) or 0,
        "tickets": db.scalar(select(func.count()).select_from(Ticket)) or 0,
    }

@app.get("/api/authors")
def list_authors(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    # Development-only seed verification endpoint. Protect/remove before deployment.
    authors = db.scalars(select(Author).order_by(Author.name)).all()
    return [{"author_id": a.author_id, "name": a.name, "email": a.email, "book_count": len(a.books)} for a in authors]
    
@app.get("/api/auth/me")
def get_my_account(
    current_user: UserAccount = Depends(get_current_user),
):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "author_id": current_user.author_id,
    }

@app.get("/api/author/books")
def get_my_books(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("author")),
):
    if not current_user.author_id:
        raise HTTPException(
            status_code=403,
            detail="This account is not linked to an author.",
        )

    books = db.scalars(
        select(Book)
        .where(Book.author_id == current_user.author_id)
        .order_by(Book.title)
    ).all()

    return [
        {
            "book_id": book.book_id,
            "title": book.title,
            "isbn": book.isbn,
            "genre": book.genre,
            "publication_date": book.publication_date,
            "status": book.status,
            "mrp": book.mrp,
            "total_copies_sold": book.total_copies_sold,
            "total_royalty_earned": book.total_royalty_earned,
            "royalty_paid": book.royalty_paid,
            "royalty_pending": book.royalty_pending,
            "last_royalty_payout_date": book.last_royalty_payout_date,
            "print_partner": book.print_partner,
        }
        for book in books
    ]

@app.get("/api/author/tickets")
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("author")),
):
    if not current_user.author_id:
        raise HTTPException(
            status_code=403,
            detail="This account is not linked to an author.",
        )

    tickets = db.scalars(
        select(Ticket)
        .where(Ticket.author_id == current_user.author_id)
        .order_by(Ticket.ticket_id.desc())
    ).all()

    return [
        {
            "ticket_id": ticket.ticket_id,
            "book_id": ticket.book_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }
        for ticket in tickets
    ]

@app.post("/api/author/tickets", status_code=201)
def create_my_ticket(
    payload: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("author")),
):
    if not current_user.author_id:
        raise HTTPException(
            status_code=403,
            detail="This account is not linked to an author.",
        )

    # If a book is supplied, verify that it belongs to this author.
    if payload.book_id:
        book = db.scalar(
            select(Book).where(
                Book.book_id == payload.book_id,
                Book.author_id == current_user.author_id,
            )
        )

        if book is None:
            raise HTTPException(
                status_code=404,
                detail="Book not found for this author.",
            )

    now = datetime.now(timezone.utc).isoformat()

    ticket = Ticket(
        author_id=current_user.author_id,
        book_id=payload.book_id,
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        category=payload.category,
        priority="Medium",
        status="Open",
        assigned_to=None,
        created_at=now,
        updated_at=now,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "message": "Support ticket created successfully.",
        "ticket_id": ticket.ticket_id,
        "subject": ticket.subject,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "created_at": ticket.created_at,
    }

@app.get("/api/admin/tickets")
def list_all_tickets(
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    query = select(Ticket)

    if status:
        query = query.where(Ticket.status == status)

    if category:
        query = query.where(Ticket.category == category)

    if priority:
        query = query.where(Ticket.priority == priority)

    tickets = db.scalars(
        query.order_by(Ticket.created_at.desc())
    ).all()

    return [
        {
            "ticket_id": ticket.ticket_id,
            "author_id": ticket.author_id,
            "book_id": ticket.book_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }
        for ticket in tickets
    ]

@app.patch("/api/admin/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    payload: TicketAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    ticket.assigned_to = payload.assigned_to.strip()
    ticket.updated_at = datetime.now(timezone.utc).isoformat()

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket assigned successfully.",
        "ticket_id": ticket.ticket_id,
        "assigned_to": ticket.assigned_to,
        "updated_at": ticket.updated_at,
    }
@app.patch("/api/admin/tickets/{ticket_id}/update")
def update_ticket(
    ticket_id: int,
    payload: TicketUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    updates = payload.model_dump(exclude_none=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide a status or priority to update.",
        )

    if "status" in updates:
        ticket.status = updates["status"]

    if "priority" in updates:
        ticket.priority = updates["priority"]

    ticket.updated_at = datetime.now(timezone.utc).isoformat()

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket updated successfully.",
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
        "priority": ticket.priority,
        "updated_at": ticket.updated_at,
    }
@app.post("/api/author/tickets/{ticket_id}/replies", status_code=201)
def author_reply(
    ticket_id: int,
    payload: TicketReplyRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("author")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None or ticket.author_id != current_user.author_id:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    reply = TicketReply(
        ticket_id=ticket.ticket_id,
        sender_role="author",
        message=payload.message.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    db.add(reply)
    ticket.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(reply)

    return {
        "message": "Reply added successfully.",
        "reply_id": reply.reply_id,
        "ticket_id": reply.ticket_id,
        "sender_role": reply.sender_role,
        "message_text": reply.message,
        "created_at": reply.created_at,
    }

@app.post("/api/admin/tickets/{ticket_id}/replies", status_code=201)
def admin_reply(
    ticket_id: int,
    payload: TicketReplyRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    reply = TicketReply(
        ticket_id=ticket.ticket_id,
        sender_role="admin",
        message=payload.message.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    db.add(reply)
    ticket.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(reply)

    return {
        "message": "Reply added successfully.",
        "reply_id": reply.reply_id,
        "ticket_id": reply.ticket_id,
        "sender_role": reply.sender_role,
        "message_text": reply.message,
        "created_at": reply.created_at,
    }
@app.get("/api/author/tickets/{ticket_id}/replies")
def author_view_replies(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("author")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None or ticket.author_id != current_user.author_id:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    replies = db.scalars(
        select(TicketReply)
        .where(TicketReply.ticket_id == ticket_id)
        .order_by(TicketReply.reply_id)
    ).all()

    return [
        {
            "reply_id": reply.reply_id,
            "sender_role": reply.sender_role,
            "message": reply.message,
            "created_at": reply.created_at,
        }
        for reply in replies
    ]
@app.post("/api/author/tickets/{ticket_id}/replies", status_code=201)

@app.post("/api/admin/tickets/{ticket_id}/notes", status_code=201)
def add_internal_note(
    ticket_id: int,
    payload: InternalNoteRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    note = InternalNote(
        ticket_id=ticket.ticket_id,
        admin_email=current_user.email,
        note=payload.note.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "message": "Internal note added successfully.",
        "note_id": note.note_id,
        "ticket_id": note.ticket_id,
        "admin_email": note.admin_email,
        "note": note.note,
        "created_at": note.created_at,
    }
@app.get("/api/admin/tickets/{ticket_id}/notes")
def view_internal_notes(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    notes = db.scalars(
        select(InternalNote)
        .where(InternalNote.ticket_id == ticket_id)
        .order_by(InternalNote.note_id)
    ).all()

    return [
        {
            "note_id": note.note_id,
            "admin_email": note.admin_email,
            "note": note.note,
            "created_at": note.created_at,
        }
        for note in notes
    ]
def fallback_ticket_suggestions(ticket: Ticket) -> dict:
    """Provide basic rule-based suggestions when AI is unavailable."""

    text = f"{ticket.subject} {ticket.description}".lower()

    if any(word in text for word in ["royalty", "payment", "payout", "invoice"]):
        category = "Royalty & Payments"
    elif any(word in text for word in ["isbn", "metadata", "book title"]):
        category = "ISBN & Metadata Issues"
    elif any(word in text for word in ["printing", "print quality", "damaged"]):
        category = "Printing & Quality"
    elif any(word in text for word in ["distribution", "availability", "store"]):
        category = "Distribution & Availability"
    elif any(word in text for word in ["production", "publishing status", "book status"]):
        category = "Book Status & Production Updates"
    else:
        category = "General Inquiry"

    if any(word in text for word in ["urgent", "immediately", "critical", "deadline today"]):
        priority = "Urgent"
    elif any(word in text for word in ["cannot", "unable", "blocked", "failed", "error"]):
        priority = "High"
    elif any(word in text for word in ["delay", "pending", "issue", "problem"]):
        priority = "Medium"
    else:
        priority = "Low"

    draft = (
        f"Hello, thank you for contacting BookLeaf Support regarding "
        f"'{ticket.subject}'. Our team will review your request and "
        f"follow up with you. Please share any additional details that "
        f"may help us investigate."
    )

    return {
        "suggested_category": category,
        "suggested_priority": priority,
        "response_draft": draft,
        "ai_mode": "fallback",
    }


@app.post("/api/admin/tickets/{ticket_id}/ai-assist")
def ai_assist_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_role("admin")),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        result = fallback_ticket_suggestions(ticket)
        result["message"] = (
            "AI service is not configured. Rule-based suggestions were returned."
        )
        return result

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You assist BookLeaf support staff. Analyze support "
                        "tickets and return only valid JSON with keys "
                        "suggested_category, suggested_priority, response_draft. "
                        "Categories must be one of: Royalty & Payments, "
                        "ISBN & Metadata Issues, Printing & Quality, "
                        "Distribution & Availability, "
                        "Book Status & Production Updates, General Inquiry. "
                        "Priorities must be Low, Medium, High, or Urgent. "
                        "Draft a polite, professional reply. Do not claim that "
                        "an action has been completed unless the ticket states so."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "subject": ticket.subject,
                        "description": ticket.description,
                        "current_category": ticket.category,
                        "current_priority": ticket.priority,
                    }),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        result = json.loads(response.choices[0].message.content)

        allowed_categories = {
            "Royalty & Payments",
            "ISBN & Metadata Issues",
            "Printing & Quality",
            "Distribution & Availability",
            "Book Status & Production Updates",
            "General Inquiry",
        }
        allowed_priorities = {"Low", "Medium", "High", "Urgent"}

        if (
            result.get("suggested_category") not in allowed_categories
            or result.get("suggested_priority") not in allowed_priorities
            or not isinstance(result.get("response_draft"), str)
            or not result["response_draft"].strip()
        ):
            raise ValueError("AI returned invalid suggestions.")

        result["ai_mode"] = "openai"
        result["message"] = (
            "Suggestions generated. Review them before updating the ticket or sending a reply."
        )
        return result

    except Exception:
        result = fallback_ticket_suggestions(ticket)
        result["message"] = (
            "AI service was unavailable or returned an invalid response. "
            "Rule-based suggestions were returned instead."
        )
        return result





