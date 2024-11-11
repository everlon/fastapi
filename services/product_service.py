from operator import or_
from fastapi import HTTPException
from http import HTTPStatus
from datetime import datetime

from sqlalchemy.orm import Session

from models.product import Product
from schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductStatusEnum,
    ProductResponse,
    ProductUpdate)


status_map = {
    "em estoque": ProductStatusEnum.in_stock,
    "em reposição": ProductStatusEnum.restocking,
    "em falta": ProductStatusEnum.out_of_stock,
}


async def map_status(status_str: str) -> ProductStatusEnum:
    status = status_map.get(status_str)

    if not status:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Status inválido.")

    return status


async def create_product(product_data: ProductCreate, db: Session) -> Product:
    status = await map_status(product_data.status.value)

    new_product = Product(
        name = product_data.name,
        description = product_data.description,
        price = product_data.price,
        status = status,
        stock_quantity = product_data.stock_quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


async def list_products(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    search: str = None,
    status: str = None
):
    query = db.query(Product)

    if search:
        query = query.filter(
            or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"))
            )
    if status:
        query = query.filter(Product.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    products = query.offset(offset).limit(page_size).all()

    return products, total


async def get_product_by_id(id: int, db: Session) -> Product:

    return db.query(Product).filter(Product.id == id).first()


async def update_product(id: int, product_data: ProductUpdate, db: Session) -> Product:
    db_product = db.query(Product).filter(Product.id == id).first()

    if not db_product:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Produto não encontrado")

    if product_data.name is not None:
        db_product.name = product_data.name
    if product_data.description is not None:
        db_product.description = product_data.description
    if product_data.price is not None:
        db_product.price = product_data.price
    if product_data.status is not None:
        db_product.status = product_data.status
    if product_data.stock_quantity is not None:
        db_product.stock_quantity = product_data.stock_quantity

    db_product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_product)

    return db_product

async def delete_product(id: int, db: Session) -> None:
    db_product = db.query(Product).filter(Product.id == id).first()

    if not db_product:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Produto não encontrado")

    db.delete(db_product)
    db.commit()
