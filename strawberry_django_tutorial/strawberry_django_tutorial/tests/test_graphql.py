import pytest
from django.test import Client
from django.urls import reverse

from book.models import Book


@pytest.fixture
def client():
    return Client()

@pytest.fixture
def create_books(db):
    Book.objects.create(title="Book 1", author="Author 1", published_date="2023-01-01")
    Book.objects.create(title="Book 2", author="Author 2", published_date="2023-01-02")


@pytest.mark.django_db
def test_books_query(client, create_books):
    query = """
    query {
        books {
            title
            author
            publishedDate
        }
    }
    """
    response = client.post(reverse("graphql"), {"query": query}, content_type="application/json")
    assert response.status_code == 200
    data = response.json()["data"]["books"]
    assert len(data) == 2
    assert data[0]["title"] == "Book 1"
    assert data[1]["title"] == "Book 2"


@pytest.mark.django_db
def test_add_book_mutation(client):
    mutation = """
    mutation {
        createBook(data: {title: "New Book", author: "New Author", publishedDate: "2023-05-01"}) {
            title
            author
            publishedDate
        }
    }
    """
    response = client.post(reverse("graphql"), {"query": mutation}, content_type="application/json")
    assert response.status_code == 200
    data = response.json()["data"]["createBook"]
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"
    assert data["publishedDate"] == "2023-05-01"
    assert Book.objects.filter(title="New Book").exists()


@pytest.mark.django_db
def test_update_book_mutation(client, create_books):
    book = Book.objects.first()
    mutation = f"""
    mutation {{
        updateBook(bookId: {book.id}, data: {{title: "Updated Book"}}) {{
            __typename
            ... on BookType {{
                title
                author
                publishedDate
            }}
            ... on Error {{
                message
            }}
        }}
    }}
    """
    response = client.post(reverse("graphql"), {"query": mutation}, content_type="application/json")
    assert response.status_code == 200
    data = response.json()["data"]["updateBook"]
    assert data["title"] == "Updated Book"
    assert data["author"] == book.author
    assert data["publishedDate"] == str(book.published_date)
    assert Book.objects.filter(title="Updated Book").exists()
    assert not Book.objects.filter(title="Book 1").exists()
    assert Book.objects.filter(title="Book 2").exists()
    assert Book.objects.count() == 2


@pytest.mark.django_db
def test_delete_book_mutation(client, create_books):
    book = Book.objects.first()
    mutation = f"""
    mutation {{
        deleteBook(bookId: {book.id}) {{
            __typename
            ... on Success {{
                result
            }}
            ... on Error {{
                message
            }}
        }}
    }}
    """
    response = client.post(reverse("graphql"), {"query": mutation}, content_type="application/json")
    assert response.status_code == 200
    data = response.json()["data"]["deleteBook"]
    assert data["result"]
    assert not Book.objects.filter(title=book.title).exists()
    assert Book.objects.count() == 1