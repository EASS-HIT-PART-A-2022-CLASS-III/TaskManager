from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from schemas.project_schema import ProjectCreate, ProjectShow
from models import User
from sqlalchemy.orm import Session
from database import get_db
from core import dependencies as d
from core import crud

router = APIRouter(tags=["project"], prefix="/project")


@router.post("/create/", response_model=ProjectShow)
def create_project(
    project: ProjectCreate,
    curr_user: User = Depends(d.get_current_user),
    db: Session = Depends(get_db),
):
    new_project = crud.create_project(db, curr_user, project)
    return new_project


@router.put("/{project_id}/add/user", response_model=ProjectShow)
def project_add_user(
    project_id: int,
    email_to_add: EmailStr,
    curr_user: User = Depends(d.get_current_user_manager),
    db: Session = Depends(get_db),
):
    user_to_add = crud.get_user_by_email(db, email_to_add)
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user don't exist"
        )
    if crud.is_project_member(db, user_to_add.id, project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user already exists in project",
        )
    return crud.add_user_to_project(db, user_to_add, project_id)


@router.put("/{project_id}/add/manager", response_model=ProjectShow)
def project_add_manager(
    project_id: int,
    email_to_add: EmailStr,
    curr_user: User = Depends(d.get_current_user_manager),
    db: Session = Depends(get_db),
):
    user_to_add = crud.get_user_by_email(db, email_to_add)
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user don't exist"
        )
    if crud.is_project_manager(db, user_to_add.id, project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user already manager in project",
        )
    return crud.add_manager_to_project(db, user_to_add, project_id)


@router.delete("/{project_id}/delete/user", response_model=ProjectShow)
def project_delete_user(
    project_id: int,
    email_to_delete: EmailStr,
    curr_user: User = Depends(d.get_current_user_manager),
    db: Session = Depends(get_db),
):
    user_to_delete = crud.get_user_by_email(db, email_to_delete)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user don't exist"
        )
    if not (crud.is_project_member(db, user_to_delete.id, project_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user don't exists in project",
        )
    return crud.remove_user_from_project(db, user_to_delete, project_id)


@router.delete("/{project_id}/")
def delete_project(
    project_id: int,
    curr_user: User = Depends(d.get_current_user_owner),
    db: Session = Depends(get_db),
):
    return crud.delete_project(db, project_id)


@router.get("/my-projects/", response_model=list[ProjectShow])
def user_projects(
    curr_user: User = Depends(d.get_current_user), db: Session = Depends(get_db)
):
    return curr_user.my_projects


@router.get("/{project_id}/", response_model=ProjectShow)
def user_project(
    project_id: int,
    curr_user: User = Depends(d.get_current_user_member),
    db: Session = Depends(get_db),
):
    return crud.get_project_by_id(db, project_id)
