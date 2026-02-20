"""
Database Models - ORM (Object-Relational Mapping)

SQLAlchemy ORM permite escrever SQL usando classes Python.

CONCEITOS:
1. BASE: Classe base que registra modelos para criação de tabelas
2. MODEL: Classe Python que representa uma tabela no banco
3. COLUMN: Classe Python que representa uma coluna na tabela
4. Tipos: String, Integer, DateTime, UUID, Text, etc

FLUXO:
1. Definir classe <heredityNode Base>
2. SQLAlchemy gera CREATE TABLE
3. Instâncias da classe = linhas no banco

EXEMPLO: Classe Book
```
class Book(Base):
    __tablename__ = "books"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    ...
```

Gera SQL:
```
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    ...
)
```

USO:
```
# Criar livro em memória
book = Book(title="...", author="...", isbn="...")

# Salvar no banco
db.add(book)
db.commit()

# Buscar do banco
book = db.query(Book).filter(Book.id == some_id).first()

# Atualizar
book.title = "New Title"
db.commit()

# Deletar
db.delete(book)
db.commit()
```

VANTAGENS DO ORM:
- SQL gerado automaticamente
- Type safety (Python types)
- Previne SQL injection
- Queries legíveis em Python
- Relationships (FK automáticas)

DESVANTAGENS:
- Performance complexa (N+1 queries)
- SQL complexo é mais lento
- Curva de aprendizado
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Book(Base):
    """
    Modelo ORM para tabela BOOKS.
    
    Representação Python de uma linha na tabela books.
    SQLAlchemy gera automaticamente:
    1. CREATE TABLE books (...)
    2. INSERT, SELECT, UPDATE, DELETE
    
    MAPEAMENTO TABELA:
    Python class Book <→> PostgreSQL table books
    
    CAMPOS:
    """
    
    __tablename__ = "books"  # Nome da tabela no banco SQL
    
    # UUID (Universally Unique Identifier)
    # PRIMARY KEY: Identificador único
    # UUID vs INT: UUID é melhor para distribuído, INT é mais rápido
    # default=uuid.uuid4: Gerar UUID automaticamente se não informado
    # index=True: Cria índice para buscas rápidas
    id = Column(
        UUID(as_uuid=True),  # Tipo: UUID (PostgreSQL native)
        primary_key=True,    # PRIMARY KEY
        default=uuid.uuid4,  # Gera UUID automaticamente
        index=True           # Criar índice para busca_rápida
    )
    
    # TITLE do livro
    # String(255): VARCHAR(255) - máximo 255 caracteres
    # nullable=False: NOT NULL - obrigatório
    # index=True: Criar índice para busca por título
    title = Column(String(255), nullable=False, index=True)
    
    # AUTHOR do livro
    # String(255): VARCHAR(255)
    # index=True: Criar índice (buscas por autor são comuns)
    author = Column(String(255), nullable=False, index=True)
    
    # ISBN
    # String(20): ISBN 10 tem 10 dígitos, ISBN 13 tem 13
    # nullable=False: NOT NULL - obrigatório
    # unique=True: UNIQUE - não pode repetir (regra de negócio)
    # index=True: Criar índice (procuramos por ISBN frequentemente)
    isbn = Column(String(20), nullable=False, unique=True, index=True)
    
    # DESCRIPTION
    # Text: Tipo para texto longo (melhor que String para grandes textos)
    # nullable=True: Pode ser NULL - é opcional
    # Sem index=True: Não buscar por descrição (seria lento em LIKE)
    description = Column(Text, nullable=True)
    
    # PAGES (número de páginas)
    # Integer: INT - número inteiro
    # nullable=True: Opcional
    pages = Column(Integer, nullable=True)
    
    # PUBLISHED_YEAR (ano de publicação)
    # Integer: INT
    # nullable=True: Pode não saber o ano
    published_year = Column(Integer, nullable=True)
    
    # CREATED_AT (quando foi criado)
    # DateTime: TIMESTAMP - data e hora
    # nullable=False: Sempre preenchido
    # default=datetime.utcnow: Usar atual quando criar
    # Nota: utcnow (não utcnow()) para não chamar na definição
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # UPDATED_AT (quando foi modificado)
    # DateTime: TIMESTAMP
    # default: Preencher com atual na criação
    # onupdate: Preencher com atual a cada UPDATE
    # Exemplo: UPDATE books SET title='...' → updated_at atualiza sozinho
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        """
        Representação textual para debug.
        Quando fazer print(livro), mostra isso.
        """
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"
