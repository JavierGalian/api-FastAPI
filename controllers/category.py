from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.category_models import Category
from controllers.auth import oauth2_scheme
from schemas.category_schemas import PostCategory, PutCategory
from models.category_models import Category

from config.db import get_db

category = APIRouter()

@category.get("/api/category", status_code=status.HTTP_200_OK)
def get_category(db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para obtener todas las categorías.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI a través de la dependencia get_db.
        token (str): Token de autenticación JWT inyectado por FastAPI a través de la dependencia oauth2_scheme.

    Returns:
        List[Category]: Lista de todas las categorías en la base de datos.
    """
    category = db.query(Category).all()

    return category

@category.post("/api/category/add-category", status_code=status.HTTP_201_CREATED)
def post_category(category : PostCategory, db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para agregar una nueva categoría.

    Args:
        category (PostCategory): Esquema de la categoría que se va a agregar.
        db (Session): Sesión de base de datos inyectada por FastAPI a través de la dependencia get_db.
        token (str): Token de autenticación JWT inyectado por FastAPI a través de la dependencia oauth2_scheme.

    Returns:
        Category: La nueva categoría agregada a la base de datos.
    """
    
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="error null")
    
    db_category = db.query(Category).filter(Category.name == category.name).first()

    if db_category.name == category.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="categoria existente")

    new_category = Category(**category.model_dump())

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
    except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al agregar categoria: " + str(e)
            )

    return new_category

@category.put("/api/category/update-category", status_code=status.HTTP_202_ACCEPTED)
def put_category(category: PutCategory, db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para actualizar una categoría existente.

    Args:
        category (PutCategory): Esquema de la categoría que se va a actualizar.
        db (Session): Sesión de base de datos inyectada por FastAPI a través de la dependencia get_db.
        token (str): Token de autenticación JWT inyectado por FastAPI a través de la dependencia oauth2_scheme.

    Returns:
        Category: La categoría actualizada.
    """
    
    db_category = db.query(Category).filter(category.name == category.old_name).first()

    db_category.name = category.new_name

    try:
        db.execute(db_category)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al agregar categoria: " + str(e)
            )
    
    return db_category

@category.delete("/api/category/delete-category", status_code=status.HTTP_200_OK)
def delete_category(category: PostCategory, db : Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
    """
    Endpoint para eliminar una categoría existente.

    Args:
        category (PostCategory): Esquema de la categoría que se va a eliminar.
        db (Session): Sesión de base de datos inyectada por FastAPI a través de la dependencia get_db.
        token (str): Token de autenticación JWT inyectado por FastAPI a través de la dependencia oauth2_scheme.

    Returns:
        dict: Mensaje de confirmación de eliminación.
    """
    db_category = db.query(Category).filter(category.name == category.name).first()

    try:
        db.delete(db_category)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la tarea la categoria: " + str(e)
            )
    return {"detail":"category delete"}