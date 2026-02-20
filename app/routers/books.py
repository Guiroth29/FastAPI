"""
API Routers para Endpoints de Livros

Este arquivo define todas as rotas (endpoints) da API para gerenciar livros.
Cada rota mapeia uma requisição HTTP para uma função que processa it.

ESTRUTURA:
1. GET /books/ → list_books() - Lista todos livros (pagination)
2. GET /books/search → search_books() - Busca por texto
3. GET /books/{id} → get_book() - Busca um livro por ID
4. POST /books/ → create_book() - Cria novo livro
5. PUT /books/{id} → update_book() - Atualiza livro completo
6. PATCH /books/{id} → partial_update_book() - Atualiza parcialmente
7. DELETE /books/{id} → delete_book() - Deleta livro

FLUXO DE UMA REQUISIÇÃO:
1. Cliente: POST /books/ com JSON {"title": "...", "author": "...", ...}
2. FastAPI:
   - Recebe requisição
   - Encontra rota correta (create_book)
   - Valida JSON com BookCreate schema (Pydantic)
   - Se válido, chama create_book()
3. Função create_book():
   - Recebe db (Session injetada via Depends)
   - Cria BookService(db)
   - Chama service.create_book()
4. BookService.create_book():
   - Valida regras de negócio (ISBN único)
   - Cria Book ORM no banco
5. Resposta:
   - Converte Book ORM → BookResponse (Pydantic)
   - Retorna JSON + status 201

CHAVES IMPORTANTES:
- async vs def: async para I/O-bound, def para CPU-bound
- Query(), Path() Parameters: Validação automática
- status_code: Status HTTP correto (201 para criação, 204 para delete)
- response_model: Schema Pydantic para resposta
- Depends(get_session): Injeção de dependência do banco
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies import get_session
from app.schemas import (
    BookResponse,
    BookCreate,
    BookUpdate,
    PaginatedBooksResponse,
)
from app.services.book_service import BookService

# Criar roteador com prefixo
# Prefixo "/books" significa todas rotas aqui começam com /books
# tags: para documentação (faz grupo na UI do Swagger)
router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Não encontrado"}},
)


@router.get("/", response_model=PaginatedBooksResponse)
async def list_books(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_session),
) -> PaginatedBooksResponse:
    """
    Listar todos os livros com paginação (ENDPOINT ASSÍNCRONO).
    
    PARÂMETROS:
    - page: Número da página (padrão: 1, mín: 1)
    - page_size: Livros por página (padrão: 10, máx: 100)
    - db: Session do banco injetada automaticamente
    
    O QUE ACONTECE:
    1. FastAPI valida parâmetros (page >= 1?, page_size >= 1?)
    2. FastAPI injeta Session do banco via Depends(get_session)
    3. BookService busca livros com paginação
    4. Retorna JSON com livros + metadados (total_pages, total_records)
    
    STATUS HTTP:
    - 200: Sucesso (padrão para GET)
    
    EXEMPLO:
    GET /books/?page=2&page_size=5
    Retorna: página 2, com 5 livros por página
    
    ASSÍNCRONO:
    - async permite processar múltiplas requisições enquanto aguarda banco
    - Melhor performance em I/O-bound operations
    """
    service = BookService(db)
    books, total = service.get_books(page=page, page_size=page_size)
    
    # Calcular total de páginas
    # Exemplo: 25 livros, 10 por página = 3 páginas
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
    q: str = Query(..., min_length=1, description="Termo de busca"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_session),
) -> PaginatedBooksResponse:
    """
    Search books by title or author (SYNC endpoint).
    
    Returns paginated search results.
    """
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
async def get_book(
    book_id: UUID,
    db: Session = Depends(get_session),
) -> BookResponse:
    """
    Get a book by ID (ASYNC endpoint).
    
    Args:
        book_id: Book UUID
        
    Returns:
        Book details
        
    Raises:
        404: Livro não encontrado
    """
    service = BookService(db)
    book = service.get_book_by_id(str(book_id))
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado",
        )
    
    return BookResponse.model_validate(book)


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_session),
) -> BookResponse:
    """
    Criar novo livro (ENDPOINT SÍNCRONO).
    
    FLUXO COMPLETO:
    1. Cliente envia: POST /books/ com JSON
       {
         "title": "Clean Code",
         "author": "Robert C. Martin",
         "isbn": "978-0132350884",
         "description": "...",
         "pages": 464,
         "published_year": 2008
       }
    
    2. FastAPI:
       - Recebe JSON
       - Valida com Pydantic schema BookCreate
         * Checa se title tem min 1 caractere
         * Checa se author tem min 1 caractere
         * Checa se isbn tem min 10 caracteres (ISBN válido)
       - Se inválido: retorna 400 Bad Request
       - Se válido: passa como book_data
    
    3. Função create_book():
       - Injeção de dependência: db = Session do banco
       - Cria BookService(db) que gerencia operações
       - Chama service.create_book(book_data)
    
    4. BookService.create_book():
       - Checa se ISBN já existe (BusinessRule)
       - Se existe: lança ValueError("ISBN already exists")
       - Se não existe:
         * Cria modelo ORM Book
         * INSERT no banco PostgreSQL
         * COMMIT transaction
         * Retorna livro criado
    
    5. Resposta:
       - Converte ORM → BookResponse (Pydantic)
       - Transforma campos Python → JSON
       - Retorna com status HTTP 201 (Created)
    
    EXCEÇÕES:
    - ValueError: ISBN duplicado → HTTP 400
    - Validation error (Pydantic) → HTTP 422
    
    SÍNCRONO:
    - def (não async) porque SQL é síncrono
    - Não bloqueia outras requisições (uvicorn em workers)
    """
    service = BookService(db)
    
    try:
        # Cria livro: validação de regra de negócio (ISBN único)
        book = service.create_book(book_data)
        # Converte ORM para Pydantic schema para serialização JSON
        return BookResponse.model_validate(book)
    except ValueError as e:
        # Se ISBN duplicado, retorna 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_session),
) -> BookResponse:
    """
    Update a book (ASYNC endpoint).
    
    Args:
        book_id: UUID do livro
        book_data: Dados de atualização do livro
        
    Returns:
        Livro atualizado
        
    Raises:
        404: Livro não encontrado
    """
    service = BookService(db)
    book = service.update_book(str(book_id), book_data)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado",
        )
    
    return BookResponse.model_validate(book)


@router.patch("/{book_id}", response_model=BookResponse)
def patch_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_session),
) -> BookResponse:
    """
    Partially update a book (SYNC endpoint - PATCH).
    
    Args:
        book_id: UUID do livro
        book_data: Dados parciais de atualização
        
    Returns:
        Livro atualizado
        
    Raises:
        404: Livro não encontrado
    """
    service = BookService(db)
    book = service.update_book(str(book_id), book_data)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado",
        )
    
    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    db: Session = Depends(get_session),
) -> None:
    """
    Deletar um livro (ENDPOINT ASSÍNCRONO).
    
    Args:
        book_id: UUID do livro
        
    Raises:
        404: Livro não encontrado
    """
    service = BookService(db)
    deleted = service.delete_book(str(book_id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado",
        )
