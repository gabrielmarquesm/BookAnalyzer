from pathlib import Path
from ..database import SessionLocal

UPLOAD_DIR = Path("../../uploads")
ALLOWED_EXTENSIONS = [".pdf"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
