from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime


class ProductStatusEnum(str, Enum):
    in_stock = "em estoque"
    restocking = "em reposição"
    out_of_stock = "em falta"


class ProductCreate(BaseModel):
    name: str = Field(..., description="Nome do produto", max_length=100)
    description: Optional[str] = Field(None, description="Descrição do produto", max_length=500)
    price: float = Field(..., gt=0, description="Preço do produto")
    status: ProductStatusEnum = Field(..., description="Status do produto")
    stock_quantity: int = Field(..., ge=0, description="Quantidade em estoque do produto")

    class Config:
        orm_mode = True


class ProductResponse(ProductCreate):
    id: int = Field(..., description="ID do produto")
    active: bool = Field(..., description="Se o produto está ativo")
    created_at: datetime = Field(..., description="Data e hora de criação do produto")
    updated_at: Optional[datetime] = Field(None, description="Data e hora de alteração do produto")


class ProductByIdResponse(BaseModel):
    product: ProductResponse
    views: list


class ProductListResponse(BaseModel):
    name: str = Field(..., description="Nome do produto", max_length=100)
    description: Optional[str] = Field(None, description="Descrição do produto", max_length=500)
    price: float = Field(..., gt=0, description="Preço do produto")
    # status: Optional[ProductStatusEnum] = Field(None, description="Status do produto")


class PaginatedProductResponse(BaseModel):
    products: List[ProductListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome do produto", max_length=100)
    description: Optional[str] = Field(None, description="Descrição do produto", max_length=500)
    price: Optional[float] = Field(None, gt=0, description="Preço do produto")
    status: Optional[ProductStatusEnum] = Field(None, description="Status do produto")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Quantidade em estoque do produto")

    class Config:
        from_attributes = True
