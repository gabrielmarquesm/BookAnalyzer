from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..error_messages import ErrorMessages
from ..models.users import Users
from ..schemas.users import UserVerification
from ..utils.utils import get_db
from .auth import get_current_user

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.INVALID_USER
        )

    if not bcrypt.checkpw(
        user_verification.password.encode(), user_model.hashed_password.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.PASSWORD_CHANGE,
        )

    password = user_verification.new_password.encode()
    salt = bcrypt.gensalt()

    user_model.hashed_password = bcrypt.hashpw(password, salt).decode()
    db.add(user_model)
    db.commit()
