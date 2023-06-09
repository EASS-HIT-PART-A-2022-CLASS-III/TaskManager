from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user_schema import UserCreate, UserShow
from schemas.token_schema import Token
from typing import Annotated
from sqlalchemy.orm import Session
from database import get_db
from core import crud, dependencies
from models import User

router = APIRouter(tags=["user"], prefix="/user")


@router.post("/create/", response_model=UserShow)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    elif crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already registered",
        )
    else:
        new_user = crud.create_user(db, user)
        return new_user


@router.post("/login/", response_model=Token)
def user_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = dependencies.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = dependencies.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=UserShow)
def user_details(curr_user: User = Depends(dependencies.get_current_user)):
    return curr_user
