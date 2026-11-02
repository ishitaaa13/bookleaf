import json
import sys
from datetime import date
from pathlib import Path

# Allows running this script from the backend directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, engine, SessionLocal
from app.models import Author, Book

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "bookleaf_sample_data.json"

def parse_date(value):
    if not value:
        return None
    return date.fromisoformat(value)

def seed():
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for author_data in payload.get("authors", []):
            author = db.get(Author, author_data["author_id"])
            if author is None:
                author = Author(
                    author_id=author_data["author_id"],
                    name=author_data["name"],
                    email=author_data["email"].lower(),
                    phone=author_data.get("phone"),
                    city=author_data.get("city"),
                    joined_date=parse_date(author_data.get("joined_date")),
                )
                db.add(author)
            else:
                author.name = author_data["name"]
                author.email = author_data["email"].lower()
                author.phone = author_data.get("phone")
                author.city = author_data.get("city")
                author.joined_date = parse_date(author_data.get("joined_date"))

            for book_data in author_data.get("books", []):
                book = db.get(Book, book_data["book_id"])
                fields = {
                    "author_id": author_data["author_id"],
                    "title": book_data["title"],
                    "isbn": book_data.get("isbn"),
                    "genre": book_data.get("genre"),
                    "publication_date": parse_date(book_data.get("publication_date")),
                    "status": book_data["status"],
                    "mrp": book_data.get("mrp"),
                    "author_royalty_per_copy": book_data.get("author_royalty_per_copy"),
                    "total_copies_sold": book_data.get("total_copies_sold") or 0,
                    "total_royalty_earned": book_data.get("total_royalty_earned") or 0,
                    "royalty_paid": book_data.get("royalty_paid") or 0,
                    "royalty_pending": book_data.get("royalty_pending") or 0,
                    "last_royalty_payout_date": parse_date(book_data.get("last_royalty_payout_date")),
                    "print_partner": book_data.get("print_partner"),
                    "available_on_json": json.dumps(book_data.get("available_on", []), ensure_ascii=False),
                }
                if book is None:
                    db.add(Book(book_id=book_data["book_id"], **fields))
                else:
                    for key, value in fields.items():
                        setattr(book, key, value)

        db.commit()
        print(f"Seeded/updated {len(payload.get('authors', []))} authors.")
        print(f"Seeded/updated {sum(len(a.get('books', [])) for a in payload.get('authors', []))} books.")
        print("Safe to rerun: existing records are updated instead of duplicated.")

if __name__ == "__main__":
    seed()
