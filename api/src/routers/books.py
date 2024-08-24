import os
import shutil
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from ..error_messages import ErrorMessages
from ..models.books import Books
from ..services.rag import answer_question, load_pdf_to_documents
from ..utils import get_db
from .auth import get_current_user

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

UPLOAD_DIR = Path("../../uploads")
ALLOWED_EXTENSIONS = [".pdf"]


class BookRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=1000)

    @field_validator("file_path")
    def validate_file_extension(cls, value):
        if not any(value.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValueError()
        return value

    model_config = ConfigDict(str_strip_whitespace=True)


class BookResponse(BaseModel):
    id: UUID
    title: str
    file_path: str


def create_user_directory(username: str):
    user_folder = UPLOAD_DIR / username
    user_folder.mkdir(parents=True, exist_ok=True)
    return user_folder


def save_file(file: UploadFile, folder: Path):
    filename = file.filename
    if filename is None or filename.strip() == "":
        return {
            "filename": "<unknown>",
            "status": "error",
            "message": "Filename is missing",
        }

    try:
        BookRequest(file_path=filename)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ErrorMessages.INVALID_FILE_EXTENSION.value}: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_path = folder / filename

    if file_path.exists():
        return {
            "filename": filename,
            "status": "skipped",
            "message": "File already exists",
        }

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": filename,
            "status": "saved",
            "message": "File saved successfully",
        }
    except Exception as e:
        return {
            "filename": filename,
            "status": "error",
            "message": f"Failed to save file: {str(e)}",
        }


@router.post("/book", status_code=status.HTTP_201_CREATED)
async def upload_book(
    user: user_dependency,
    db: db_dependency,
    files: Annotated[list[UploadFile], File()],
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.NO_FILE_PROVIDED,
        )

    user_folder = create_user_directory(user["username"])
    status_messages = []

    for file in files:
        result = save_file(file, user_folder)
        status_messages.append(result)

        if result["status"] == "saved":
            book_model = Books(
                title=file.filename,
                file_path=str(user_folder / file.filename),  # type: ignore
                owner_id=user.get("id"),
            )
            try:
                db.add(book_model)
                db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save {file.filename} to the database",
                )

    return {"status": status_messages}


@router.get("/books", response_model=list[BookResponse])
async def read_books(
    user: user_dependency,
    db: db_dependency,
    title: str | None = None,
):
    query = db.query(Books).filter(Books.owner_id == user.get("id"))

    if title:
        query = query.filter(Books.title.ilike(f"%{title}%"))

    books = query.all()

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No books found"
        )

    return books


@router.get("/books/{book_id}", response_model=BookResponse)
async def read_book(book_id: UUID, user: user_dependency, db: db_dependency):
    book = (
        db.query(Books)
        .filter(Books.id == book_id, Books.owner_id == user.get("id"))
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    user: user_dependency,
    db: db_dependency,
):

    book = (
        db.query(Books)
        .filter(Books.id == book_id, Books.owner_id == user.get("id"))
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    try:
        db.delete(book)
        db.commit()

        file_path = book.file_path

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Warning: File {file_path} does not exist")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while trying to delete the book in the database",
        )


@router.post("/books/{book_id}/ask")
async def ask_question(
    book_id: str, question: str, user: user_dependency, db: db_dependency
):
    book = (
        db.query(Books)
        .filter(Books.id == book_id, Books.owner_id == user.get("id"))
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    answer = answer_question(book.file_path, question)
    return {"answer": answer}
