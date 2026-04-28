from fastapi import FastAPI
from typing import Optional

app = FastAPI(
    title="Bella Tavola API",
    description="API do restaurante Bella Tavola",
    version="1.0.0"
)
pratos = [
    {"id": 1, "nome": "Calabreza", "categoria": "pizza", "preco": 45.0},
    {"id": 2, "nome": "Fettuccine ao Sugo", "categoria": "massa", "preco": 52.0},
    {"id": 3, "nome": "Nhoque (Ginocchi) ao Molho Branco", "categoria": "massa", "preco": 58.0},
    {"id": 4, "nome": "Cannoli", "categoria": "sobremesa", "preco": 28.0},
    {"id": 5, "nome": "Franco com Catupiry", "categoria": "pizza", "preco": 49.0},
    {"id": 6, "nome": "Palha Italiana", "categoria": "sobremesa", "preco": 24.0},
]

@app.get("/pratos")
async def listar_pratos():
    return pratos


@app.get("/pratos/{prato_id}")
async def buscar_prato(prato_id: int):
    for prato in pratos:
        if prato["id"] == prato_id:
            return prato
    return {"mensagem": "Prato não encontrado"}


@app.get("/pratos")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False
):
    resultado = pratos
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado
