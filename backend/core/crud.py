from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, Project, project_managers, project_users, Task
from schemas.user_schema import UserCreate, UserShow
from schemas.project_schema import ProjectCreate
from schemas.task_schema import TaskCreate, TaskUpdate
from core import hashing


# read
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter_by(email=email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter_by(username=username).first()


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter_by(id=project_id).first()


def get_project_tasks(db: Session, project_id: int) -> list[Task] | None:
    return get_project_by_id(db, project_id).tasks


def get_project_task(db: Session, project_id: int, task_id: int) -> Task:
    return db.query(Task).filter_by(id=task_id, project_id=project_id).first()


def is_project_owner(db: Session, user_id: int, project_id: int) -> bool:
    return (
        db.query(Project).filter_by(creator_id=user_id, id=project_id).first()
        is not None
    )


def is_project_manager(db: Session, user_id: int, project_id: int) -> bool:
    return (
        db.query(User)
        .join(project_managers)
        .filter_by(user_id=user_id, project_id=project_id)
        .first()
        is not None
    )


def is_project_member(db: Session, user_id: int, project_id: int) -> bool:
    return (
        db.query(User)
        .join(project_users)
        .filter_by(user_id=user_id, project_id=project_id)
        .first()
        is not None
    )


# create


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hashing.get_password_hash(user.password)
    new_user = User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_project(db: Session, user: UserShow, project: ProjectCreate) -> Project:
    new_project = Project(
        title=project.title, description=project.description, creator_id=user.id
    )
    new_project.users.append(user)
    new_project.managers.append(user)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def create_task(
    db: Session, project_id: int, task: TaskCreate, curr_user: UserShow
) -> Task:
    new_task = Task(**task.dict(), project_id=project_id, created_by_id=curr_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# update
def add_user_to_project(db: Session, user_to_add: User, project_id: int):
    project = get_project_by_id(db, project_id)
    project.users.append(user_to_add)
    db.commit()
    db.refresh(project)
    return project


def add_manager_to_project(db: Session, user_to_add: User, project_id: int):
    project = get_project_by_id(db, project_id)
    if user_to_add not in project.users:
        project.users.append(user_to_add)
    project.managers.append(user_to_add)
    db.commit()
    db.refresh(project)
    return project


def update_task(
    db: Session, project_id: int, task_id: int, task_data: TaskUpdate
) -> Task | None:
    task = get_project_task(db, project_id, task_id)
    if task is None or task.project_id != project_id:
        return None

    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


# delete


def remove_user_from_project(
    db: Session, user_to_remove: User, project_id: int
) -> Project:
    project = get_project_by_id(db, project_id)
    if user_to_remove.id == project.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't remove project owner",
        )

    project.users.remove(user_to_remove)
    if user_to_remove in project.managers:
        project.managers.remove(user_to_remove)

    db.query(Task).filter_by(
        project_id=project_id, created_by_id=user_to_remove.id
    ).update({Task.created_by_id: None}, synchronize_session="fetch")
    db.query(Task).filter_by(
        project_id=project_id, assignee_id=user_to_remove.id
    ).update({Task.assignee_id: None}, synchronize_session="fetch")

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int):
    project = get_project_by_id(db, project_id)
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully."}


def remove_task_from_project(db: Session, Task_to_remove: Task, project_id: int):
    db.delete(Task_to_remove)
    db.commit()
    return {"message": "Task removed from project successfully."}
