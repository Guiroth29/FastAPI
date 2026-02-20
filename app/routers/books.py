"""Book routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_session
from app.schemas import BookCreate, BookResponse, BookUpdate, PaginatedBooksResponse
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"], responses={404: {"description": "Not found"}})


@router.get("/", response_model=PaginatedBooksResponse)
async def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_session),
) -> PaginatedBooksResponse:
    service = BookService(db)
    books, total = service.get_books(page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedBooksResponse(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total,
        data=[BookResponse.model_validate(book) for book in books],
    )


@router.get("/search", response_model=PaginatedBooksResponse)
def search_books(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_session),
) -> PaginatedBooksResponse:
    service = BookService(db)
    books, total = service.search_books(query=q, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedBooksResponse(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total,
        data=[BookResponse.model_validate(book) for book in books],
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: UUID, db: Session = Depends(get_session)) -> BookResponse:
    service = BookService(db)
    book = service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    return BookResponse.model_validate(book)


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, db: Session = Depends(get_session)) -> BookResponse:
    service = BookService(db)
    try:
        book = service.create_book(book_data)
        return BookResponse.model_validate(book)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_session),
) -> BookResponse:
    service = BookService(db)
    try:
        book = service.update_book(book_id, book_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    return BookResponse.model_validate(book)


@router.patch("/{book_id}", response_model=BookResponse)
def patch_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_session),
) -> BookResponse:
    service = BookService(db)
    try:
        book = service.update_book(book_id, book_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, db: Session = Depends(get_session)) -> None:
    service = BookService(db)
    deleted = service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
