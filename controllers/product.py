from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update

from models.products_models import Product
from schemas.product_schemas import ProductPost, ProductPut, ProductDelete
from utils.auth.authenticate_user import get_user_disabled_current
from schemas.user_schemas import UserModelGet

from config.db import get_db

product = APIRouter()

@product.get("/api/product", status_code=status.HTTP_200_OK)
def get_product(db : Session = Depends(get_db)):
    product = db.query(Product).all()

    return product

@product.post("/api/produtc/create-product", status_code= status.HTTP_201_CREATED)
def post_product(product : ProductPost, db : Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    product_dict = product.model_dump()

    for value in product_dict.values():
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="formulario incompleto"
            )
    if (product_dict["stock"] <= 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error stock no puede ser cero"
        )
    product_dict["user_id"] = user.id
    new_product = Product(**product_dict)
    
    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al agregar producto: " + str(e)
            )
    return new_product

@product.put("/api/product/update-product", status_code=status.HTTP_202_ACCEPTED)
def update_product(product : ProductPut, db : Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    update_product = update(Product).where(Product.user_id == user.id and Product.sku == product.sku).values(product.model_dump())

    try:
        db.execute(update_product)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar producto: " + str(e)
            )
    
@product.delete("api/product/delete-product" , status_code= status.HTTP_200_OK)
def delete_product(sku_product : ProductDelete, db : Session = Depends(get_db), user : UserModelGet = Depends(get_user_disabled_current)):

    delete_product = db.query(Product).filter(Product.sku == sku_product.sku and Product.user_id == user.id).first()

    try:
        db.delete(delete_product)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la tarea Producto: " + str(e)
            )    