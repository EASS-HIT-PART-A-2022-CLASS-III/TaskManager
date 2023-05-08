from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from schemas.task_schema import TaskCreate, TaskShow, TaskUpdate
from models import User
from sqlalchemy.orm import Session
from database import get_db
import crud
from dependencies import get_current_user_manager, get_current_user_member


router = APIRouter(tags=["task"], prefix= "/project/{project_id}/task")

@router.post("/", response_model=TaskShow)
def create_task(project_id: int, task: TaskCreate,
                curr_user:User = Depends(get_current_user_manager),db: Session = Depends(get_db)):
    new_task = crud.create_task(db, project_id,task,curr_user)
    return jsonable_encoder(new_task)

@router.get("/", response_model=list[TaskShow])
def read_tasks(project_id: int,
               curr_user:User = Depends(get_current_user_member),db: Session = Depends(get_db)):
    return crud.get_project_tasks(db, project_id)

@router.get("/{task_id}", response_model=TaskShow)
def read_task(project_id: int,task_id: int,
              curr_user:User = Depends(get_current_user_member),db: Session = Depends(get_db)):
    return jsonable_encoder(crud.get_project_task(db, project_id,task_id))

@router.delete("/{task_id}")
def delete_task(project_id: int, task_id: int,
                curr_user:User = Depends(get_current_user_manager),db: Session = Depends(get_db)):
    task = crud.get_project_task(db,project_id,task_id)
    if not task or (task.project_id != project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in the project")
    return crud.remove_task_from_project(db, task, project_id)

@router.put("/{task_id}", response_model=TaskShow)
def update_task(project_id: int, task_id: int, task_data:TaskUpdate,
                curr_user:User = Depends(get_current_user_member), db: Session = Depends(get_db)):
    if task_data.assignee_id is not None:
        if not crud.is_project_member(db,task_data.assignee_id,project_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be a member of the project")
    updated_task = crud.update_task(db,project_id, task_id, task_data)
    if updated_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in the project")
    return jsonable_encoder(updated_task)