FROM python:3.12-slim

WORKDIR /bevi

COPY pyproject.toml poetry.lock /

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install

COPY . /bevi

EXPOSE 8000

CMD ["uvicorn", "bevi_products.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
