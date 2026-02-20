import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Allows local tests without PostgreSQL/Docker.
os.environ.setdefault("USE_SQLITE_FOR_TESTS", "1")

from app.database import create_all_tables, drop_all_tables
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_all_tables()
    yield
    drop_all_tables()


@pytest.fixture(autouse=True)
def clean_database():
    drop_all_tables()
    create_all_tables()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_book() -> dict:
    return {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "isbn": "978-0134494166",
        "description": "Software architecture guide",
        "pages": 432,
        "published_year": 2017,
    }


def create_book(client: TestClient, payload: dict) -> dict:
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    return response.json()


class TestBooks:
    def test_create_book(self, client: TestClient, sample_book: dict):
        response = client.post("/books/", json=sample_book)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == sample_book["title"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_duplicate_isbn_returns_400(self, client: TestClient, sample_book: dict):
        create_book(client, sample_book)

        response = client.post("/books/", json=sample_book)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_books_uses_required_pagination_shape(self, client: TestClient, sample_book: dict):
        for index in range(3):
            payload = sample_book.copy()
            payload["isbn"] = f"978-01344941{index:02d}"
            create_book(client, payload)

        response = client.get("/books/?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()

        assert data["currentPage"] == 1
        assert data["pageSize"] == 2
        assert data["totalPages"] == 2
        assert data["totalRecords"] == 3
        assert len(data["data"]) == 2

    def test_get_book(self, client: TestClient, sample_book: dict):
        created = create_book(client, sample_book)

        response = client.get(f"/books/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_book_not_found(self, client: TestClient):
        response = client.get(f"/books/{uuid4()}")
        assert response.status_code == 404

    def test_update_book(self, client: TestClient, sample_book: dict):
        created = create_book(client, sample_book)

        response = client.patch(
            f"/books/{created['id']}",
            json={"title": "Updated title", "pages": 500},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["pages"] == 500

    def test_delete_book(self, client: TestClient, sample_book: dict):
        created = create_book(client, sample_book)

        response = client.delete(f"/books/{created['id']}")
        assert response.status_code == 204

        response = client.get(f"/books/{created['id']}")
        assert response.status_code == 404

    def test_search_books(self, client: TestClient, sample_book: dict):
        python_book = sample_book.copy()
        python_book["title"] = "Python Internals"
        python_book["isbn"] = "978-0134494100"
        create_book(client, python_book)

        java_book = sample_book.copy()
        java_book["title"] = "Java Patterns"
        java_book["isbn"] = "978-0134494101"
        create_book(client, java_book)

        response = client.get("/books/search?q=Python")
        assert response.status_code == 200
        data = response.json()
        assert data["totalRecords"] == 1
        assert data["data"][0]["title"] == "Python Internals"


class TestHealthAndRoot:
    def test_health(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in {"healthy", "unhealthy"}
        assert data["database"] in {"connected", "disconnected"}

    def test_root(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["docs"] == "/docs"
        assert data["ui"] == "/ui"
