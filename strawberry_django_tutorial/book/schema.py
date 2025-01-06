from typing import Annotated, List, Union
from dataclasses import asdict

import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry import auto

from .models import Book

@strawberry.type
class Error:
    message: str


@strawberry.type
class Success:
    result: bool


@strawberry_django.type(Book)
class BookType:
    id: auto
    title: auto
    author: auto
    published_date: auto


@strawberry_django.input(Book)
class BookUpdateInput:
    title: str | None = None
    author: str | None = None
    published_date: str | None = None


Response = Annotated[
    Union[BookType, Error],
    strawberry.union("BookResponse")
]

DeleteResponse = Annotated[
    Union[Success, Error],
    strawberry.union("DeleteResponse")
]


@strawberry.type
class Query:
    books: List[BookType] = strawberry_django.field()


@strawberry.type
class Mutation:
    create_book: BookType = strawberry_django.mutations.create(BookUpdateInput)


    @strawberry.mutation
    def update_book(self, book_id: int, data: BookUpdateInput) -> Response:
        try:
            book = Book.objects.get(id=book_id)
            for key, value in asdict(data).items():
                if value is not None:
                    setattr(book, key, value)

            book.save()

            return book
        except Book.DoesNotExist:
            return Error(message="Not Found")
        except Exception as e:
            return Error(f"An error occurred: {str(e)}")


    @strawberry.mutation
    def delete_book(self, book_id: int) -> DeleteResponse:
        try:
            book = Book.objects.get(pk=book_id)
            book.delete()

            return Success(result=True)
        except Book.DoesNotExist:
            return Error(message="Not Found")
        except Exception as e:
            return Error(f"An error occurred: {str(e)}")
    

schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=[DjangoOptimizerExtension,],)