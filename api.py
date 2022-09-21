from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


class Produtos(BaseModel):
    id: int
    q: str
    valor_minimo: int
    valor_maximo: int


banco_de_dados = [
    Produtos(id=1, q='teste', valor_minimo=10, valor_maximo=100),
    Produtos(id=2, q='teste 2', valor_minimo=10, valor_maximo=100),
    Produtos(id=3, q='teste 3', valor_minimo=10, valor_maximo=100)
]


@app.get("/")
def get_produtos():
    return banco_de_dados


@app.post("/")
def post_produtos(produtos: Produtos):
    banco_de_dados.append(produtos)
    return produtos

