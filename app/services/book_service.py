"""
Business Logic para Operações de Livro

PADRÃO SERVICE:
O padrão Service encapsula toda lógica de negócio.

POR QUÊ?
- Separação de responsabilidades
- Lógica não fica espalhada em routers
- Fácil testar
- Fácil reusar em múltiplos routers

ESTRUTURA:
APIRouter (HTTP) → Service (lógica) → ORM (banco de dados)

EXEMPLO: POST /books/
1. Router create_book() recebe JSON
2. Router valida com Pydantic
3. Router injeta Session + BookCreate
4. Router chama BookService(db).create_book(data)
5. Service valida regras de negócio (ISBN único)
6. Service altera dados ou lança exceção
7. Router retorna resposta ao cliente

MÉTODOS DO BookService:
- get_books(): Listar com paginação
- get_book_by_id(): Buscar por UUID
- get_book_by_isbn(): Buscar por ISBN (interno/rautilidade)
- create_book(): Criar novo livro (valida ISBN único)
- update_book(): Atualizar completo (PUT)
- partial_update_book(): Atualizar parcial (PATCH)
- delete_book(): Deletar
- search_books(): Buscar por texto (título/autor)
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import Book
from app.schemas import BookCreate, BookUpdate


class BookService:
    """
    Serviço para lógica de negócio de livros.
    
    RESPONSABILIDADES:
    - Validação de regras de negócio (ISBN único, etc)
    - Operações CRUD no banco
    - Buscas e filtros complexos
    
    INJATADO EM:
    - Routers via BookService(db)
    - Recebe Session do banco via Depends
    """
    
    def __init__(self, db: Session):
        """
        Inicializar serviço com sessão do banco.
        
        Args:
            db: SQLAlchemy Session (injeção de dependência)
        """
        self.db = db
    
    def get_books(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[Book], int]:
        """
        Obter livros paginados do banco de dados.
        
        Args:
            page: Número da página (1-indexed)
            page_size: Número de itens por página
            
        Returns:
            Tupla de (lista de livros, contagem total)
        """
        # Obter contagem total
        total = self.db.query(func.count(Book.id)).scalar()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Query books
        books = self.db.query(Book).order_by(desc(Book.created_at)).offset(offset).limit(page_size).all()
        
        return books, total
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """
        Get a book by ID.
        
        Args:
            book_id: UUID do livro
            
        Returns:
            Objeto Book ou None se não encontrado
        """
        return self.db.query(Book).filter(Book.id == book_id).first()
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Obter livro por ISBN.
        
        Args:
            isbn: ISBN do livro
            
        Returns:
            Objeto Book ou None se não encontrado
        """
        return self.db.query(Book).filter(Book.isbn == isbn).first()
    
    def create_book(self, book_data: BookCreate) -> Book:
        """
        Criar novo livro com validação de ISBN único.
        
        FLUXO:
        1. Validação de regra de negócio: ISBN deve ser único
        2. Converter BookCreate (Pydantic) → Book (ORM)
        3. Incluir em sessão: self.db.add()
        4. Salvar no banco: self.db.commit()
        5. Atualizar objeto: self.db.refresh()
        6. Retornar livro criado
        
        DETALHES:
        - book_data é BookCreate (validado por Pydantic)
        - book_data.model_dump() converte para dict: {"title": "...", "author": ...}
        - Book(**dict) desempacota dict em argumentos: Book(title=..., author=...)
        - self.db.add(obj) marca objeto como novo para INSERT
        - self.db.commit() executa:
          * INSERT INTO books (title, author, isbn, ...) VALUES (...)
          * COMMIT (salva transação no banco)
        - self.db.refresh(obj) faz SELECT para reatualizar objeto com:
          * id (gerado pelo banco)
          * created_at (DEFAULT CURRENT_TIMESTAMP)
          * updated_at (DEFAULT CURRENT_TIMESTAMP)
        
        EXCEÇÃO:
        - Se ISBN já existe: lança ValueError
        - Router captura com try/except
        - Retorna HTTP 400 Bad Request
        
        TRANSAÇÕES:
        - SQLAlchemy gerencia transações automaticamente
        - add() + commit() = INSERT atomicamente
        - Se erro: rollback automático
        
        Args:
            book_data: BookCreate schema (validado por Pydantic)
            
        Returns:
            Book ORM com id, created_at, updated_at preenchidos
            
        Raises:
            ValueError: Se ISBN já existe no banco
        """
        # Regra de negócio 1: ISBN deve ser único
        existing = self.get_book_by_isbn(book_data.isbn)
        if existing:
            # Lança exceção que router captura e transforma em HTTP 400
            raise ValueError(f"Book with ISBN {book_data.isbn} already exists")
        
        # Converter Pydantic schema → ORM model
        # BookCreate é um dict-like (pode fazer model_dump())
        # Book(**dict) chama: Book(title=..., author=..., isbn=..., ...)
        db_book = Book(**book_data.model_dump())
        
        # Marcar para INSERT
        self.db.add(db_book)
        
        # Executar INSERT e COMMIT (salvar)
        self.db.commit()
        
        # Atualizar objeto com dados, do banco (id, created_at, updated_at)
        # Isso faz um SELECT SELECT * FROM books WHERE id = ...
        self.db.refresh(db_book)
        
        return db_book
    
    def update_book(self, book_id: str, book_data: BookUpdate) -> Optional[Book]:
        """
        Atualizar um livro existente.
        
        Args:
            book_id: UUID do livro
            book_data: Dados de atualização do livro
            
        Returns:
            Objeto Book atualizado ou None se não encontrado
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        # Update only provided fields
        update_data = book_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)
        
        self.db.commit()
        self.db.refresh(book)
        return book
    
    def delete_book(self, book_id: str) -> bool:
        """
        Delete a book.
        
        Args:
            book_id: Book UUID
            
        Returns:
            True if deleted, False if not found
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return False
        
        self.db.delete(book)
        self.db.commit()
        return True
    
    def search_books(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[Book], int]:
        """
        Buscar livros por título ou autor.
        
        Args:
            query: String da busca
            page: Número da página (1-indexed)
            page_size: Número de itens por página
            
        Returns:
            Tupla de (lista de livros, contagem total)
        """
        search_filter = (
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%"))
        )
        
        total = self.db.query(func.count(Book.id)).filter(search_filter).scalar()
        
        offset = (page - 1) * page_size
        
        books = (
            self.db.query(Book)
            .filter(search_filter)
            .order_by(desc(Book.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return books, total
