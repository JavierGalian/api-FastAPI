from fastapi import APIRouter, Depends, status, HTTPException
from schemas.task import TasksModelPost, TasksModelGet, TaskModelDelete
from sqlalchemy.orm import Session
from models import tasks_models
from schemas.user_schemas import UserModelGet
from config.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update

from utils.auth.authenticate_user import get_user_disabled_current


tasks = APIRouter()


def parsed_object_db(data):
    """
    recibe un objeto de la base de datos y pasa a un objeto TasksModelGet proveniente de pydantic
    """
    task_model_response = TasksModelGet(

            id=data.id,
            title=data.title,
            description=data.description,
            created_at=data.created_at,
            user_id=data.user_id,
        )
    return task_model_response

#*------------------------------------METHOD GET-----------------------------------------------
@tasks.get("/task", status_code=status.HTTP_200_OK)
async def get_tasks(db: Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):
    try:
        data = db.query(tasks_models.Task).filter(tasks_models.Task.user_id == user.id).all()
        return data
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in database"+ str(e)
            )

@tasks.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(task_id:int, db: Session=Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):
    
    try:
        data = db.query(tasks_models.Task).filter(tasks_models.Task.id == task_id and tasks_models.Task.user_id == user.id).first()
        
        if data:
            #task_model_response = parsed_object_db(data)
            return data

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND id")
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error en base de datos'+ str(e)
            )



#*------------------------------------METHOD POST-----------------------------------------------
@tasks.post("/task/create-task", status_code=status.HTTP_201_CREATED)
def create_task(task:TasksModelPost, db: Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    ID_TASK_USER = 0

    if not task.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title not found")
    
    data = db.query(tasks_models.Task).filter(tasks_models.Task.user_id == user.id).all()
    for task_data in data:
        if task_data.id:
            ID_TASK_USER = task_data.id
        if task_data.title == task.title:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="title exist in data base")

    task_data = {
        "id" : ID_TASK_USER + 1,
        "title"  : task.title,
        "description" : task.description,
        "user_id" : user.id,
    }

    new_task = tasks_models.Task(**task_data)
    
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar la tarea: " + str(e)
        )

    return new_task


#*------------------------------------METHOD DELETE-----------------------------------------------
@tasks.delete("/task/delete-task")
def delete_task(title_task: TaskModelDelete, db: Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    data = db.query(tasks_models.Task).filter(tasks_models.Task.title == title_task.title and tasks_models.Task.user_id == user.id).first()
    if (data):
        try:
            db.delete(data)
            db.commit()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la tarea la tarea: " + str(e)
            )
        
        raise HTTPException(status_code=status.HTTP_200_OK, detail="success delete")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found task")


#*------------------------------------METHOD PUT-----------------------------------------------
@tasks.put("/task/update-task")
def update_task(task: TasksModelGet, db: Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    
    data = db.query(tasks_models.Task).filter(tasks_models.Task.title == task.title and tasks_models.Task.user_id == user.id).first()
    
    if (data.id != task.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="title exist in data base")
    
    update_task = update(tasks_models.Task).where(tasks_models.Task.id==task.id).values(title = task.title,description = task.description)
    try:
        db.execute(update_task)
        db.commit()
    except SQLAlchemyError as e:
        print(e)
    
    raise HTTPException(status_code=status.HTTP_200_OK, detail="ok update")

