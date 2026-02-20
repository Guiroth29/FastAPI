"""
Dependency Injection Functions

INJEÇÃO DE DEPENDÊNCIA (Dependency Injection):
Padrão de design que evita criar objetos dentro das funções.

O PROBLEMA:
```
# Ruim: cria Session a cada função
def list_books():
    db = SessionLocal()  # Criar
    books = db.query(Book).all()
    db.close()  # Fechar
    return books

def create_book(data):
    db = SessionLocal()  # Criar NOVAMENTE
    book = Book(**data)
    db.add(book)
    db.commit()
    db.close()  # Fechar NOVAMENTE
    return book
```

PROBLEMAS:
- Código repetido
- Fácil esquecer db.close()
- Difícil testar (mockar dependências é complicado)
- Acoplamento alto (função cria sua própria dependência)

A SOLUÇÃO: Injeção de Dependência
```
# Melhor: FastAPI injeta Session
@app.get("/books")
def list_books(db: Session = Depends(get_session)):
    books = db.query(Book).all()
    return books  # Sem fechar! FastAPI gerencia

@app.post("/books")
def create_book(data: BookCreate, db: Session = Depends(get_session)):
    book = Book(**data)
    db.add(book)
    db.commit()
    return book  # Sem fechar! FastAPI gerencia automaticamente
```

COMO FUNCIONA:
1. FastAPI vê get_session em Depends()
2. Chama get_session()
3. Função yield db
4. FastAPI injeta db na função
5. Função roda
6. FastAPI continua de get_session (no finally)
7. db.close() é executado automaticamente

CONTEXT MANAGER COM YIELD:
```
def get_session():
    db = SessionLocal()  # SETUP
    try:
        yield db  # Injetar em função
    finally:
        db.close()  # CLEANUP (sempre executado)
```

O YIELD é mágico:
- Tudo antes: runs BEFORE (setup)
- Yield value: INJETADO em função
- Tudo depois (finally): runs AFTER (cleanup)

BENEFÍCIOS:
- Sem repetição de código
- Cleanup garantido (finally)
- Fácil de testar (mockar é simples)
- Desacoplado
"""
from typing import Generator

from app.database import get_session as _get_db_session


def get_session() -> Generator:
    """
    Dependency para injetar Database Session.

    Usa a função `get_session` definida em `app.database` para criar a
    Session no momento da requisição (evita importar `SessionLocal`
    a partir de um valor None antes da inicialização do DB).
    """
    db = _get_db_session()
    try:
        yield db
    finally:
        db.close()
