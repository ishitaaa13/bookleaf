import sys
from pathlib import Path
from getpass import getpass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.auth import hash_password
from app.database import Base, engine, SessionLocal
from app.models import Author, UserAccount


def create_user():
    role = input("Account role (author/admin): ").strip().lower()

    if role not in {"author", "admin"}:
        print("Invalid role. Choose author or admin.")
        return

    email = input("Email: ").strip().lower()

    if not email or "@" not in email:
        print("Enter a valid email address.")
        return

    author_id = None

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing = db.scalar(
            select(UserAccount).where(UserAccount.email == email)
        )

        if existing:
            print("An account with this email already exists.")
            return

        if role == "author":
            author = db.scalar(
                select(Author).where(Author.email == email)
            )

            if author is None:
                print("No existing author has this email.")
                print("Use an email from your seeded author records.")
                return

            author_id = author.author_id

        password = getpass("Enter password (minimum 12 characters): ")

        if len(password) < 12:
            print("Password must contain at least 12 characters.")
            return

        confirm_password = getpass("Confirm password: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return

        account = UserAccount(
            email=email,
            password_hash=hash_password(password),
            role=role,
            author_id=author_id,
            is_active=1,
        )

        db.add(account)
        db.commit()

        print(f"{role.capitalize()} account created successfully.")
        print(f"Email: {email}")


if __name__ == "__main__":
    create_user()
