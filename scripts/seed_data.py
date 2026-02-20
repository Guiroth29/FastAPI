"""Seed script to populate database with initial data."""
import logging
from app.database import get_session
from app.models import Book
from datetime import datetime

logger = logging.getLogger(__name__)


def seed_books() -> None:
    """Seed the database with sample books."""
    db = get_session()
    
    # Check if books already exist
    existing = db.query(Book).first()
    if existing:
        logger.info("Database already contains books, skipping seed")
        db.close()
        return
    
    # Sample books data
    sample_books = [
        {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "978-0132350884",
            "description": "A Handbook of Agile Software Craftsmanship",
            "pages": 464,
            "published_year": 2008,
        },
        {
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "isbn": "978-0135957059",
            "description": "Your Journey to Mastery in Software Development",
            "pages": 352,
            "published_year": 2019,
        },
        {
            "title": "Design Patterns",
            "author": "Gang of Four",
            "isbn": "978-0201633610",
            "description": "Elements of Reusable Object-Oriented Software",
            "pages": 395,
            "published_year": 1994,
        },
        {
            "title": "Refactoring",
            "author": "Martin Fowler",
            "isbn": "978-0134757599",
            "description": "Improving the Design of Existing Code",
            "pages": 472,
            "published_year": 2018,
        },
        {
            "title": "The Mythical Man-Month",
            "author": "Frederick P. Brooks Jr.",
            "isbn": "978-0201835953",
            "description": "Essays on Software Engineering",
            "pages": 336,
            "published_year": 1995,
        },
        {
            "title": "Code Complete",
            "author": "Steve McConnell",
            "isbn": "978-0735619678",
            "description": "A Practical Handbook of Software Construction",
            "pages": 960,
            "published_year": 2004,
        },
    ]
    
    try:
        for book_data in sample_books:
            book = Book(**book_data)
            db.add(book)
        
        db.commit()
        logger.info(f"Successfully seeded {len(sample_books)} books")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_books()
