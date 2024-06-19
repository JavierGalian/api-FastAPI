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
    """
    Endpoint para obtener una lista de tareas del usuario autenticado.

    Este endpoint permite a un usuario recuperar todas las tareas asociadas a su cuenta.

    Parámetros:
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas.
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuesta:
        200 OK: Se devuelve una lista con las tareas del usuario en formato JSON.
        500 Internal Server Error: Error interno del servidor al intentar consultar la base de datos.

    Lógica:
        1. Recupera la información del usuario autenticado mediante la dependencia "user".
        2. Construye una consulta para recuperar todas las tareas de la base de datos 
           filtradas por el ID de usuario obtenido en el paso anterior.
        3. Ejecuta la consulta y almacena el resultado en la variable "data".
        4. En caso de éxito, devuelve la lista de tareas del usuario.
        5. Maneja posibles errores durante la consulta utilizando un bloque try-except.
           En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """
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
    """
    Endpoint para obtener una tarea específica por su ID.

    Este endpoint permite a un usuario recuperar la información de una tarea específica 
    proporcionando su ID en la ruta.

    Parámetros:
        task_id (int): ID de la tarea que se desea recuperar.
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas.
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuestas:
        200 OK: Se encontró la tarea y se devuelve la información en formato JSON.
        404 Not Found: No se encontró ninguna tarea con el ID especificado.
        500 Internal Server Error: Error interno del servidor al intentar consultar la base de datos.

    Lógica:
        1. Recupera la información del usuario autenticado mediante la dependencia "user".
        2. Construye una consulta para recuperar una tarea específica de la base de datos 
           filtrada por el ID de la tarea y el ID de usuario obtenido en el paso anterior.
        3. Ejecuta la consulta y almacena el resultado en la variable "data".
        4. Si se encuentra la tarea, la devuelve en formato JSON.
        5. Si no se encuentra la tarea, eleva una excepción HTTP indicando que no se encontró.
        6. Maneja posibles errores durante la consulta utilizando un bloque try-except.
           En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """
    
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
    """
    Endpoint para crear una nueva tarea para el usuario autenticado.

    Este endpoint permite a un usuario crear una nueva tarea asociada a su cuenta.

    Parámetros:
        task (TasksModelPost): Objeto que contiene la información de la nueva tarea 
                               (título y descripción) enviada en la solicitud.
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuesta:
        201 Created: La tarea se ha creado exitosamente y se devuelve la información de la tarea creada en formato JSON.
        400 Bad Request: La solicitud carece de un título para la tarea.
        409 Conflict: Ya existe una tarea con el mismo título para el usuario.
        500 Internal Server Error: Error interno del servidor al intentar guardar la tarea en la base de datos.

    Lógica:
        1. Recupera la información del usuario autenticado mediante la dependencia "user".
        2. Valida si se ha enviado un título para la tarea. Si no se ha enviado, se eleva una excepción HTTP indicando una solicitud incorrecta.
        3. Consulta todas las tareas existentes del usuario para verificar si ya existe una tarea con el mismo título.
        4. Itera sobre las tareas existentes del usuario:
            - Si se encuentra una tarea existente con el mismo título, se eleva una excepción HTTP indicando conflicto.
        5. Define un ID inicial para la nueva tarea (puede ser un valor inicial o una estrategia de generación de ID).
        6. Construye un diccionario con la información de la nueva tarea, incluyendo:
            - ID (utilizando el ID inicial definido anteriormente)
            - Título
            - Descripción
            - ID de usuario obtenido en el paso 1
        7. Crea una nueva instancia del modelo de tareas ("tasks_models.Task") utilizando el diccionario creado en el paso 6.
        8. Intenta guardar la nueva tarea en la base de datos utilizando un bloque try-except:
            - Agrega la nueva tarea a la sesión ("db.add(new_task)")
            - Confirma los cambios en la base de datos ("db.commit()")
            - Recarga la instancia de la tarea para obtener el ID asignado por la base de datos ("db.refresh(new_task)")
        9. En caso de éxito, devuelve la instancia de la tarea creada.
        10. Maneja posibles errores durante el guardado utilizando el bloque try-except.
             En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """

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
    """
    Endpoint para eliminar una tarea por su título.

    Este endpoint permite a un usuario eliminar una tarea específica asociada a su cuenta, 
    proporcionando el título de la tarea que se desea eliminar.

    Parámetros:
        title_task (TaskModelDelete): Objeto que contiene el título de la tarea a eliminar 
                                       enviado en la solicitud.
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuestas:
        200 OK: La tarea se ha eliminado exitosamente. Se devuelve un mensaje de confirmación ("success delete") en formato JSON.
        404 Not Found: No se encontró ninguna tarea con el título especificado para el usuario autenticado.
        500 Internal Server Error: Error interno del servidor al intentar eliminar la tarea de la base de datos.

    Lógica:
        1. Recupera la información del usuario autenticado mediante la dependencia "user".
        2. Construye una consulta para buscar una tarea específica en la base de datos 
           filtrada por el título de la tarea proporcionado en la solicitud y el ID de usuario obtenido en el paso 1.
        3. Ejecuta la consulta y almacena el resultado en la variable "data".
        4. Si se encuentra la tarea:
            - Intenta eliminar la tarea utilizando un bloque try-except:
                - Elimina la tarea de la sesión ("db.delete(data)")
                - Confirma los cambios en la base de datos ("db.commit()")
            - En caso de éxito, eleva una excepción HTTP con código 200 OK y un mensaje de confirmación.
        5. Si no se encuentra la tarea, eleva una excepción HTTP indicando que no se encontró.
        6. Maneja posibles errores durante la eliminación utilizando el bloque try-except.
             En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """

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
    """
    Endpoint para actualizar una tarea existente.

    Este endpoint permite a un usuario modificar la información de una tarea 
    asociada a su cuenta, proporcionando el ID y los nuevos datos de la tarea.

    Parámetros:
        task (TasksModelGet): Objeto que contiene el ID, título y descripción de la tarea a actualizar 
                               enviado en la solicitud.
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuestas:
        200 OK: La tarea se ha actualizado exitosamente. Se devuelve un mensaje de confirmación ("ok update") en formato JSON.
        400 Bad Request: El ID de la tarea enviada en la solicitud no coincide con el ID de la tarea encontrada en la base de datos. 
                           Esto podría indicar un intento de modificación no autorizada.
        409 Conflict: Ya existe otra tarea con el mismo título para el usuario autenticado.
        500 Internal Server Error: Error interno del servidor al intentar actualizar la tarea en la base de datos.

    Lógica:
        1. Recupera la información del usuario autenticado mediante la dependencia "user".
        2. Construye una consulta para buscar una tarea específica en la base de datos 
           filtrada por el título proporcionado en la solicitud y el ID de usuario obtenido en el paso 1.
        3. Ejecuta la consulta y almacena el resultado en la variable "data".
        4. Si se encuentra la tarea:
            - Verifica si el ID de la tarea enviada en la solicitud coincide con el ID de la tarea encontrada.
                - Si no coinciden, se eleva una excepción HTTP indicando una solicitud incorrecta (potencial intento de modificación no autorizada).
            - Verifica si ya existe otra tarea con el mismo título para el usuario:
                - Si existe, se eleva una excepción HTTP indicando conflicto.
            - Construye una consulta para actualizar la tarea utilizando la librería SQLAlchemy:
                - Define la tabla a actualizar ("tasks_models.Task")
                - Define la condición de actualización (filtrar por ID de la tarea)
                - Define los valores a actualizar (título y descripción)
        5. Intenta ejecutar la consulta de actualización utilizando un bloque try-except:
            - Ejecuta la consulta de actualización ("db.execute(update_task)")
            - Confirma los cambios en la base de datos ("db.commit()")
        6. En caso de éxito, eleva una excepción HTTP con código 200 OK y un mensaje de confirmación.
        7. Maneja posibles errores durante la actualización utilizando el bloque try-except:
            - En caso de error, se imprime el error en la consola (considera registrar el error en un log)
            - Se eleva una excepción HTTP indicando un error interno del servidor.
    """
    
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

