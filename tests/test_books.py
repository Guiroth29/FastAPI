"""
Tests para Endpoints de Livros

PYTEST: Framework de testes Python

O QUE TESTA:
- Endpoints HTTP (GET, POST, PUT, DELETE, PATCH)
- Status codes (200, 201, 400, 404)
- Formatos de resposta (JSON válido, schema correto)
- Validação de entrada (Pydantic)
- Regras de negócio (ISBN único, etc)

POR QUE TESTAR:
- Confiança que código funciona
- Refatoração segura (testes alertam se quebrou)
- Documentação viva (testes mostram como usar API)
- Regressão (testes evitam reproduzir bugs passados)

ESTRUTURA:
Fixtures → Setup compartilhado
Tests → Função que começa com test_
Assertions → assert statement == expected

EXEMPLO:
```
def test_list_books(client, db_session):
    # Setup: já feito por fixtures
    
    # Act: fazer requisição
    response = client.get("/books")
    
    # Assert: validar resultado
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
```

FIXTURES:
- setup_database: 1x por sesão (criar tabelas)
- db_session: 1x por test (limpar dados)
- client: 1x por test (TestClient)
- sample_book: 1x por test (dados fake)
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.database import SessionLocal, create_all_tables, drop_all_tables, Base
from app.models import Book


@pytest.fixture(scope="session")
def setup_database():
    """
    Fixture: Setup banco de testes (executado 1x por sessão).
    
    ESCOPO:
    - scope="session": 1x por sessão de testes (não por test)
    - Cria tabelas no início
    - Remove tabelas no fim
    
    POR QUÊ 1x:
    - Caro criar/dropar tabelas (I/O do disco)
    - Otimização: criar 1x, depois limpar dados por test
    
    YIELD:
    - Tudo antes yield: setup (CREATE TABLE)
    - Tudo depois yield: teardown (DROP TABLE)
    """
    # Criar todas tabelas
    create_all_tables()
    
    # Liberar outros fixtures (dependem deste)
    yield
    
    # Limpar: dropar todas tabelas
    drop_all_tables()


@pytest.fixture(autouse=True)
def db_session(setup_database):
    """
    Fixture: Limpar dados entre tests (executado antes de CADA test).
    
    AUTOUSE=TRUE: executar automaticamente sem mencionar em teste
    
    POR QUÊ:
    - Cada teste começa com banco limpo
    - Testes são independentes (não afetam uns aos outros)
    - Evita testes falharem por ordem de execução
    
    FLUXO:
    1. Test 1 cria livro, testa
    2. db_session limpa (DROP + CREATE)
    3. Test 2 cria livro diferente, testa
    4. db_session limpa novamente
    5. Assim por diante
    """
    # Limpar dados: dropar e recriar
    drop_all_tables()
    create_all_tables()
    
    # Liberar teste
    yield
    
    # Após teste: dropar novamente (limpar lixo do teste)
    drop_all_tables()
    create_all_tables()


@pytest.fixture
def client():
    """
    Fixture: TestClient para fazer requisições.
    
    TestClient simula client HTTP sem rodar servidor real.
    
    USO:
    client.get("/books")
    client.post("/books", json={...})
    client.delete("/books/{id}")
    
    RETORNA:
    Response object com:
    - status_code (200, 201, 400, etc)
    - json() (parsed JSON)
    - text (conteúdo raw)
    """
    return TestClient(app)


@pytest.fixture
def sample_book():
    """
    Fixture: Dados de exemplo para criar livro.
    
    Usado em múltiplos testes:
    1. test_create_book: usar sample_book
    2. test_update_book: criar com sample_book, depois atualizar
    3. test_get_book:  criar com sample_book, depois buscar
    
    DADOS:
    - title, author, isbn: obrigatórios
    - description, pages, published_year: opcionais
    - isbn valido (10-20 caracteres)
    """
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "978-0201633610",
        "description": "A test book",
        "pages": 300,
        "published_year": 2024,
    }


class TestBookEndpoints:
    """
    Testes para CRUD endpoints de livros.
    
    Organização em classe: agrupar testes relacionados
    
    PADRÃO AAA:
    1. Arrange: Preparar dados/setup
    2. Act: Fazer ação (core do teste)
    3. Assert: Validar resultado
    
    EXEMPLO: test_create_book
    1. Arrange: sample_book fixture (dados prontos)
    2. Act: client.post("/books/", json=sample_book)
    3. Assert: response.status_code == 201, data["title"] == ...
    """
    
    def test_create_book(self, client, sample_book):
        """
        Teste: Criar livro - HAPPY PATH.
        
        CENÁRIO:
        1. Cliente POST /books/ com dados válidos
        2. Servidor cria livro no banco
        3. Retorna 201 Created com livro criado
        
        VALIDAÇÕES:
        - Status HTTP 201 (Created, não 200!)
        - Campos retornados correspondem ao enviado
        - id foi gerado (UUID)
        - created_at foi preenchido (timestamp)
        
        FLUXO HTTP:
        POST /books/
        {
          "title": "Test Book",
          "author": "Test Author",
          "isbn": "978-0201633610",
          ...
        }
        
        Resposta:
        201 Created
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "title": "Test Book",
          "author": "Test Author",
          "isbn": "978-0201633610",
          "created_at": "2024-01-15T10:30:00",
          "updated_at": "2024-01-15T10:30:00",
          ...
        }
        """
        # Act: Fazer requisição POST
        response = client.post("/books/", json=sample_book)
        
        # Assert: Status code
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        # Assert: Parsear JSON
        data = response.json()
        
        # Assert: Campos obrigatórios
        assert data["title"] == sample_book["title"]
        assert data["author"] == sample_book["author"]
        assert data["isbn"] == sample_book["isbn"]
        
        # Assert: Campos generados pelo banco
        assert "id" in data  # UUID gerado
        assert "created_at" in data  # Timestamp generado
    
    def test_create_book_duplicate_isbn(self, client, sample_book):
        """
        Teste: Criar livro com ISBN duplicado - ERROR CASE.
        
        CENÁRIO:
        1. Criar primeiro livro: OK
        2. Tentar criar segundo livro com MESMO ISBN
        3. Retorna 400 Bad Request (violar unique constraint)
        
        REGRA DE NEGÓCIO:
        ISBN deve ser único (cada livro tem ISBN diferente)
        
        VALIDAÇÕES:
        - Primeiro POST /books/: sucesso 201
        - Segundo POST /books/ (mesmo ISBN): erro 400
        - Mensagem de erro menciona ISBN
        """
        # Arrange & Act: Criar primeiro livro
        response1 = client.post("/books/", json=sample_book)
        assert response1.status_code == 201
        
        # Act: Tentar criar segundo livro com MESMO ISBN
        response2 = client.post("/books/", json=sample_book)
        
        # Assert: Deve falhar com 400 (Bad Request)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_list_books(self, client, sample_book):
        """Test listing books."""
        # Create multiple books
        for i in range(3):
            book_data = sample_book.copy()
            book_data["isbn"] = f"978-020163361{i}"
            client.post("/books/", json=book_data)
        
        # List books
        response = client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert data["current_page"] == 1
        assert data["page_size"] == 10
        assert data["total_records"] == 3
        assert len(data["data"]) == 3
    
    def test_list_books_pagination(self, client, sample_book):
        """Test pagination."""
        # Create 15 books
        for i in range(15):
            book_data = sample_book.copy()
            book_data["isbn"] = f"978-020163361{i:02d}"
            client.post("/books/", json=book_data)
        
        # Get first page
        response1 = client.get("/books/?page=1&page_size=10")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total_records"] == 15
        assert data1["total_pages"] == 2
        assert len(data1["data"]) == 10
        
        # Get second page
        response2 = client.get("/books/?page=2&page_size=10")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["data"]) == 5
    
    def test_get_book(self, client, sample_book):
        """Test getting a book by ID."""
        # Create a book
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]
        
        # Get the book
        response = client.get(f"/books/{book_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == sample_book["title"]
    
    def test_get_book_not_found(self, client):
        """Test getting a non-existent book."""
        fake_id = str(uuid4())
        response = client.get(f"/books/{fake_id}")
        assert response.status_code == 404
    
    def test_update_book(self, client, sample_book):
        """Test updating a book."""
        # Create a book
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]
        
        # Update the book
        update_data = {"title": "Updated Title", "pages": 400}
        response = client.put(f"/books/{book_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["pages"] == 400
        assert data["author"] == sample_book["author"]  # Unchanged
    
    def test_patch_book(self, client, sample_book):
        """Test patching a book."""
        # Create a book
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]
        
        # Patch the book
        patch_data = {"description": "Updated description"}
        response = client.patch(f"/books/{book_id}", json=patch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
    
    def test_delete_book(self, client, sample_book):
        """Test deleting a book."""
        # Create a book
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]
        
        # Delete the book
        response = client.delete(f"/books/{book_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 404
    
    def test_search_books(self, client, sample_book):
        """Test searching books."""
        # Create books
        book1 = sample_book.copy()
        book1["isbn"] = "978-0201633610"
        book1["title"] = "Python Programming"
        book1["author"] = "Alfred Author"
        client.post("/books/", json=book1)
        
        book2 = sample_book.copy()
        book2["isbn"] = "978-0201633611"
        book2["title"] = "Java Guide"
        book2["author"] = "Bob Author"
        client.post("/books/", json=book2)
        
        # Search by title
        response = client.get("/books/search?q=Python")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 1
        assert data["data"][0]["title"] == "Python Programming"
        
        # Search by author
        response = client.get("/books/search?q=Bob")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 1
        assert data["data"][0]["author"] == "Bob Author"


class TestHealthCheck:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["status"] == "healthy"
    
    def test_healthz(self, client):
        """Test Kubernetes-style health check."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
