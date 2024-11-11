from fastapi import FastAPI, Depends

from database import Base, engine

from controllers.product_controller import router as product_router
from controllers.auth_controller import router as auth_router

from auth import get_current_active_user

version = "v1"
version_prefix =f"/api/{version}"
description = "Desenvolvimento de API CRUD de Produtos em Python"

app = FastAPI(
    title="Teste BEVI FastApi",
    description=description,
    version=version,
    contact={
        "name": "Everlon Passos",
        "url": "https://github.com/everlon",
        "email": "everlon@protonmail.com",
    },
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Veja bem-vindo(a) a nossa API!"}


app.include_router(
    product_router,
    prefix=f"{version_prefix}/products",
    tags=["products"],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    auth_router,
    prefix=f"{version_prefix}/auth",
    tags=["auth"]
)
