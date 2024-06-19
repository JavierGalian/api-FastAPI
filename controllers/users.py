
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.user_schemas import UserModelPost, UserModelGet, UserModelPut
from models import user_models
from utils.auth.authenticate_user import get_user_disabled_current, authenticate_token_jwt
from utils.auth.authenticate_email import authenticate_email

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update

from controllers.auth import oauth2_scheme 

users = APIRouter()



#*------------------------------------METHOD GET-----------------------------------------------
# def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     data = db.query(user_models.UserModels).order_by(user_models.UserModels.id).all()
#     return data

# @users.get("/user", status_code=status.HTTP_200_OK)
# async def get_user(users : UserModelGet = Depends(current_user)):
#     return users


@users.get("/user/me", status_code=status.HTTP_200_OK)
async def get_user_me(user : UserModelGet = Depends(get_user_disabled_current)):
    """
    Endpoint para obtener los datos del usuario autenticado.

    Este endpoint permite a un usuario recuperar su propia información de 
    perfil asociada a la sesión activa.

    Parámetros:
        user (UserModelGet): Dependencia que recupera la información del usuario autenticado.

    Respuesta:
        200 OK: Se devuelven los datos del usuario autenticado en formato JSON.
    """

    # Devuelve la información del usuario obtenido mediante la dependencia
    return user

#*------------------------------------METHOD POST-----------------------------------------------
@users.post("/user/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModelPost, db: Session = Depends(get_db)):
    """
    Endpoint para crear un nuevo usuario.

    Este endpoint permite registrar a un nuevo usuario en la aplicación.

    Parámetros:
        user (UserModelPost): Objeto que contiene los datos del nuevo usuario 
                             enviados en la solicitud (generalmente como JSON).
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.

    Respuesta:
        201 Created: El usuario se ha creado exitosamente y se devuelve un mensaje de confirmación 
                     en formato JSON. Adicionalmente, se puede devolver el resultado 
                     de la función `authenticate_email` (asumiendo que se encarga de enviar 
                     un correo electrónico de bienvenida o verificación).

        406 Not Acceptable: La solicitud carece de alguno de los datos necesarios para crear el usuario.

        500 Internal Server Error: Error interno del servidor al intentar guardar 
                                    el usuario en la base de datos.

    Lógica:
        1. Recorre los atributos del objeto "user" para verificar si alguno de ellos es None (nulo).
            - Si se encuentra un atributo nulo, se eleva una excepción HTTP indicando que la información está incompleta.
        2. Convierte el objeto "user" a un diccionario utilizando el método "model_dump" 
           (asumiendo que este método está definido en el modelo UserModelPost).
        3. Crea una nueva instancia del modelo de usuarios ("user_models.UserModels") 
           desempaquetando el diccionario creado en el paso 2.
        4. Intenta guardar el nuevo usuario en la base de datos utilizando un bloque try-except:
            - Agrega el nuevo usuario a la sesión ("db.add(new_user)")
            - Confirma los cambios en la base de datos ("db.commit()")
            - Recarga la instancia del usuario para obtener el ID asignado por la base de datos ("db.refresh(new_user)")
        5. En caso de éxito, guarda el resultado de la función `authenticate_email` 
           (asumiendo que se encarga de enviar un correo electrónico de bienvenida o verificación).
        6. Devuelve un diccionario con un mensaje de confirmación ("created ok") 
           y el resultado de la función `authenticate_email` (opcional).
        7. Maneja posibles errores durante el guardado utilizando el bloque try-except.
             En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """

    for key, value in user.__dict__.items():
        if value is None:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'data incomplet {key}')
        
    user_data = user.model_dump() #convert user to dictionary

    
    new_user = user_models.UserModels(**user_data)  # Unpack the dictionary

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )

    send_email_user = authenticate_email(**user_data)

    return ({"message": "created ok"}, send_email_user)

#*------------------------------------METHOD PUT-----------------------------------------------

@users.put("/user/update-user", status_code=status.HTTP_200_OK)
async def update_user(user : UserModelPut, db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para actualizar la información de un usuario.

    Este endpoint permite a un usuario modificar su propia información de perfil 
    asociada al token de autenticación JWT proporcionado.

    Parámetros:
        user (UserModelPut): Objeto que contiene los nuevos datos del usuario 
                             enviados en la solicitud (generalmente como JSON).
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        token (str): Token de autenticación JWT obtenido de la solicitud.

    Respuesta:
        200 OK: La información del usuario se ha actualizado exitosamente y se devuelve un mensaje de confirmación 
                 en formato JSON.

        401 Unauthorized: El token de autenticación JWT es inválido o ha expirado.

        500 Internal Server Error: Error interno del servidor al intentar actualizar la información del usuario en la base de datos.

    Lógica:
        1. Valida el token de autenticación JWT utilizando la función `authenticate_token_jwt`.
            - Si el token es inválido o ha expirado, se eleva una excepción HTTP indicando que no está autorizado.
        2. Recupera la información del usuario autenticado a partir del token válido.
        3. Construye una consulta para actualizar la información del usuario en la base de datos utilizando la librería SQLAlchemy:
            - Define la tabla a actualizar ("user_models.UserModels")
            - Define la condición de actualización (filtrar por ID de usuario obtenido del token)
            - Define los valores a actualizar utilizando el método "model_dump" del objeto "user" 
              (asumiendo que convierte los datos del usuario a un diccionario).
        4. Intenta ejecutar la consulta de actualización utilizando un bloque try-except:
            - Ejecuta la consulta de actualización ("db.execute(user_current_modify)")
            - Confirma los cambios en la base de datos ("db.commit()")
        5. En caso de éxito, devuelve un diccionario con un mensaje de confirmación ("message":"modify ok").
        6. Maneja posibles errores durante la actualización utilizando el bloque try-except.
             En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.
    """

    user_current = authenticate_token_jwt(token, db)

    user_current_modify = update(user_models.UserModels).where(user_models.UserModels.id==user_current.id).values(user.model_dump())
    try:
        db.execute(user_current_modify)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )

    return ({"message":"modify ok"})

#*------------------------------------METHOD DELETE-----------------------------------------------
@users.delete("/user/delete", status_code=status.HTTP_200_OK)
async def delete_user(db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para eliminar a un usuario.

    Este endpoint permite a un usuario eliminar su propia cuenta asociada 
    al token de autenticación JWT proporcionado.

    Parámetros:
        db (Session): Dependencia que inyecta una sesión de la base de datos para realizar consultas y modificaciones.
        token (str): Token de autenticación JWT obtenido de la solicitud.

    Respuesta:
        200 OK: La cuenta del usuario se ha eliminado exitosamente y se devuelve un mensaje de confirmación 
                 en formato JSON.

        401 Unauthorized: El token de autenticación JWT es inválido o ha expirado.

        500 Internal Server Error: Error interno del servidor al intentar eliminar al usuario de la base de datos.

    Lógica:
        1. Valida el token de autenticación JWT utilizando la función `authenticate_token_jwt`.
            - Si el token es inválido o ha expirado, se eleva una excepción HTTP indicando que no está autorizado.
        2. Recupera la información del usuario autenticado a partir del token válido.
        3. Intenta eliminar al usuario utilizando un bloque try-except:
            - Elimina al usuario de la sesión ("db.delete(user_current)").
            - Confirma los cambios en la base de datos ("db.commit()").
        4. En caso de éxito, devuelve un diccionario con un mensaje de confirmación ("message":"ok delete").
        5. Maneja posibles errores durante la eliminación utilizando el bloque try-except.
             En caso de error, se eleva una excepción HTTP indicando un error interno del servidor.

        """

    user_current = authenticate_token_jwt(token, db)

    try:
        db.delete(user_current)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: " + str(e)
            )
    
    return ({"message":"ok delete"})