import shutil
from enum import Enum
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from ..error_messages import ErrorMessages
from ..schemas.books import BookRequest
from .utils import ALLOWED_EXTENSIONS


class FileStatus(str, Enum):
    SAVED = "saved"
    SKIPPED = "skipped"
    ERROR = "error"
    UNKNOWN = "unknown"


class FileMessages(str, Enum):
    SAVED_SUCCESSFULLY = "File saved successfully"
    ALREADY_EXISTS = "File already exists"
    FILENAME_MISSING = "Filename is missing"
    FAILED_TO_SAVE = "Failed to save file"


def create_response(
    filename: str, status: FileStatus, message: FileMessages
) -> dict[str, str]:
    return {"filename": filename, "status": status.value, "message": message.value}


def validate_filename(filename: str) -> str:
    if not filename or filename.strip() == "":
        raise ValueError(FileMessages.FILENAME_MISSING.value)
    return filename


def validate_file_extension(filename: str) -> None:
    try:
        BookRequest(file_path=filename)
    except ValueError:
        allowed_extensions = ", ".join(ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ErrorMessages.INVALID_FILE_EXTENSION.value}: {allowed_extensions}",
        )


def save_file_content(file: UploadFile, file_path: Path) -> None:
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def save_file(file: UploadFile, folder: Path) -> dict[str, str]:
    filename = file.filename or "<unknown>"

    try:
        filename = validate_filename(filename)
        validate_file_extension(filename)
    except ValueError as e:
        return create_response(
            "<unknown>", FileStatus.ERROR, FileMessages.FILENAME_MISSING
        )
    except HTTPException as http_exc:
        raise http_exc

    file_path = Path(folder / filename)

    if file_path.exists():
        return create_response(
            filename, FileStatus.SKIPPED, FileMessages.ALREADY_EXISTS
        )

    try:
        save_file_content(file, file_path)
        return create_response(
            filename, FileStatus.SAVED, FileMessages.SAVED_SUCCESSFULLY
        )
    except Exception as e:
        return create_response(filename, FileStatus.ERROR, FileMessages.FAILED_TO_SAVE)
