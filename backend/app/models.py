from sqlalchemy import String, Integer, Float, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    joined_date: Mapped[Date | None] = mapped_column(Date, nullable=True)

    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.author_id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(64), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(160), nullable=True)
    publication_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    mrp: Mapped[float | None] = mapped_column(Float, nullable=True)
    author_royalty_per_copy: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_copies_sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_royalty_earned: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    royalty_paid: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    royalty_pending: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    last_royalty_payout_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    print_partner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    available_on_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="book")

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.author_id"), index=True, nullable=False)
    book_id: Mapped[str | None] = mapped_column(ForeignKey("books.book_id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="General Inquiry", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="Medium", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Open", nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)

    author: Mapped["Author"] = relationship(back_populates="tickets")
    book: Mapped["Book | None"] = relationship(back_populates="tickets")
    replies: Mapped[list["TicketReply"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    notes: Mapped[list["InternalNote"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")

class TicketReply(Base):
    __tablename__ = "ticket_replies"

    reply_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.ticket_id"), index=True, nullable=False)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="replies")

class InternalNote(Base):
    __tablename__ = "internal_notes"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.ticket_id"), index=True, nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="notes")

class UserAccount(Base):
    __tablename__ = "user_accounts"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="author", nullable=False)
    author_id: Mapped[str | None] = mapped_column(
        ForeignKey("authors.author_id"), unique=True, nullable=True
    )
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
