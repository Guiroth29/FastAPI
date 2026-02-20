"""
Schemas Pydantic para Validação de Requisição/Resposta

PYDANTIC é uma biblioteca que valida dados usando type hints.

O QUE FAZ PYDANTIC:
1. Valida tipos (int, str, UUID, etc)
2. Valida limites (min_length, max_length, ge, le, etc)
3. Converte tipos (JSON string → UUID, datetime, etc)
4. Valida regras customizadas (@field_validator)
5. Auto-serializa para JSON
6. Auto-deserializa de JSON

FLUXO DE VALIDAÇÃO:
Cliente envia JSON → FastAPI → Pydantic valida → Função recebe dados válidos

EXEMPLO COM BookCreate:
JSON de entrada:
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "description": "...",
  "pages": "464",  # String!
  "published_year": 2008
}

Pydantic:
1. Checa title: é string? Sim ✓ | Comprimento > 0? Sim ✓
2. Checa author: é string? Sim ✓ | Comprimento > 0? Sim ✓
3. Checa isbn: é string? Sim ✓ | Comprimento >= 10? Sim ✓
4. Checa pages: é int? Não (é string) → converte "464" → 464 ✓ | Valor >= 1? Sim ✓
5. Tudo válido! ✓

Se algum falho:
{
  "title": "",  # Erro: min_length=1 mas length=0
}
Resposta HTTP 422:
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character"
    }
  ]
}

SCHEMAS NESTE PROJETO:
1. BookBase - Campos comuns entre Create e Update
2. BookCreate - Herda BookBase (usado em POST)
3. BookUpdate - Todos campos opcionais (usado em PUT/PATCH)
4. BookResponse - Com timestamps (depois de salvar no banco)
5. PaginatedBooksResponse - Lista paginada
6. HealthCheckResponse - Status da API
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class BookBase(BaseModel):
    """
    Esquema base com campos comuns do livro.
    Herança: BookCreate e BookUpdate herdam daqui.
    
    VALIDAÇÕES:
    - title: obrigatório, string, 1-255 caracteres
    - author: obrigatório, string, 1-255 caracteres
    - isbn: obrigatório, string, 10-20 caracteres (ISBN 10/13)
    - description: opcional, string
    - pages: opcional, inteiro >= 1
    - published_year: opcional, inteiro
    """
    title: str = Field(..., min_length=1, max_length=255, description="Título do livro")
    author: str = Field(..., min_length=1, max_length=255, description="Nome do autor")
    isbn: str = Field(..., min_length=10, max_length=20, description="ISBN")
    description: Optional[str] = Field(None, description="Descrição do livro")
    pages: Optional[int] = Field(None, ge=0, description="Número de páginas")
    published_year: Optional[int] = Field(None, description="Ano de publicação")


class BookCreate(BookBase):
    """
    Esquema para CRIAR livro.
    Herda todos campos de BookBase (todos obrigatórios).
    Usado em: POST /books/
    
    Fluxo:
    1. JSON → Pydantic valida com BookCreate
    2. Se válido, função recebe book_data: BookCreate
    3. Para usar em banco: alterar para modelo ORM Book
    """
    pass


class BookUpdate(BaseModel):
    """
    Esquema para ATUALIZAR livro.
    Todos campos OPCIONAIS (pode atualizar só alguns).
    Usado em: PUT /books/{id} (atualização completa, mas campos opcionais)
                  PATCH /books/{id} (atualização parcial)
    
    Validações (iguais a BookBase, MAS todos Optional):
    - title: opcional, se presente deve ter 1-255 caracteres
    - author: opcional, se presente deve ter 1-255 caracteres
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    pages: Optional[int] = Field(None, ge=0)
    published_year: Optional[int] = None


class BookResponse(BookBase):
    """Schema for book response."""
    id: UUID = Field(..., description="Book ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    current_page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    total_records: int = Field(..., ge=0, description="Total number of records")


class PaginatedBooksResponse(BaseModel):
    """Resposta de livros paginada."""
    current_page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)
    total_records: int = Field(..., ge=0)
    data: List[BookResponse] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    """Resposta de verificação de saúde da API."""
    status: str = Field(..., description="Status da aplicação")
    database: str = Field(..., description="Status da conexão com banco")
