from http import HTTPStatus

# from pydantic import version
import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db

from bevi_products.main import app


# Configuração do banco de dados de teste.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Substituir a dependência get_db com a versão de teste
app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

version_prefix = "/api/v1/products"


def login_token():
    # Efetuar login para obter Token
    response = client.post("/api/v1/auth/token", data={"username": "everlon", "password": "secret"})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return {"Authorization": f"Bearer {data["access_token"]}"}


def test_create_product():
    product_data = {
        "name": "Produto de Teste",
        "description": "Descrição do Produto teste",
        "price": 99.99,
        "status": "em estoque",
        "stock_quantity": 10
    }

    response = client.post(f"{version_prefix}/", json=product_data, headers=login_token())

    assert response.status_code == HTTPStatus.CREATED, f"Erro: {response.text}"

    response_data = response.json()
    assert response_data["name"] == product_data["name"]
    assert response_data["description"] == product_data["description"]
    assert response_data["price"] == product_data["price"]
    assert response_data["status"] == "em estoque"
    assert response_data["stock_quantity"] == product_data["stock_quantity"]
    assert response_data["active"] is True
    assert "created_at" in response_data


def test_list_products():
    client.post(f"{version_prefix}/", json={
        "name": "Produto Teste",
        "description": "Descrição do produto",
        "price": 99.99,
        "status": "em estoque",
        "stock_quantity": 20
    }, headers=login_token())

    response = client.get(f"{version_prefix}/", headers=login_token())

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert len(response.json()) > 0


def test_get_product_by_id():
    # Criar um produto para garantir que a lista não esteja vazia
    response = client.post(f"{version_prefix}/", json={
        "name": "Produto Teste",
        "description": "Descrição do produto",
        "price": 99.99,
        "status": "em estoque",
        "stock_quantity": 20
    }, headers=login_token())

    assert response.status_code == HTTPStatus.CREATED
    product_id = response.json()["id"]

    response = client.get(f"{version_prefix}/{product_id}", headers=login_token())
    assert response.status_code == HTTPStatus.OK
    assert response.json()["product"]["name"] == "Produto Teste"

    # Acessar a lista para registrar no LOG do MongoDB
    response_views = client.get(f"{version_prefix}/", headers=login_token())
    assert response_views.status_code == HTTPStatus.OK

    # Verificar se o LOG foi registrado acessando o Produto novamente pelo ID
    # e verificando se existe os Views.
    response_get_views = client.get(f"{version_prefix}/{product_id}", headers=login_token())
    assert response_get_views.status_code == HTTPStatus.OK
    assert "views" in response_get_views.json()
    assert len(response_get_views.json()["views"]) > 0


def test_update_product():
    # Criar um produto para garantir que a lista não esteja vazia
    response = client.post(f"{version_prefix}/", json={
        "name": "Produto Teste Atualização",
        "description": "Descrição do produto para atualização",
        "price": 49.99,
        "status": "em estoque",
        "stock_quantity": 50
    }, headers=login_token())

    assert response.status_code == HTTPStatus.CREATED
    product_id = response.json()["id"]

    update_data = {
        "name": "Produto Atualizado",
        "price": 89.99,
        "status": "em reposição",
        "stock_quantity": 30
    }
    response = client.put(f"{version_prefix}/{product_id}", json=update_data, headers=login_token())
    assert response.status_code == HTTPStatus.OK

    updated_product = response.json()
    assert updated_product["name"] == "Produto Atualizado"
    assert updated_product["price"] == 89.99
    assert updated_product["status"] == "em reposição"
    assert updated_product["stock_quantity"] == 30


def test_delete_product():
    # Criar um produto para garantir que a lista não esteja vazia
    response = client.post(f"{version_prefix}/", json={
        "name": "Produto Teste Deleção",
        "description": "Descrição do produto para deleção",
        "price": 29.99,
        "status": "em estoque",
        "stock_quantity": 10
    }, headers=login_token())

    assert response.status_code == HTTPStatus.CREATED
    product_id = response.json()["id"]

    response = client.delete(f"{version_prefix}/{product_id}", headers=login_token())
    assert response.status_code == HTTPStatus.NO_CONTENT
    # assert response.json() == {"detail": "Produto deletado com sucesso"}

    response = client.get(f"{version_prefix}/{product_id}", headers=login_token())
    assert response.status_code == HTTPStatus.NOT_FOUND
    # assert response.json() == {"detail": "Produto não encontrado"}
