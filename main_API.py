from fastapi import FastAPI

app = FastAPI(
    title="Bella Tavola API",
    description="API do restaurante Bella Tavola",
    version="1.0.0"
)
pratos = [
    {"id": 1, "nome": "Margherita", "categoria": "pizza", "preco": 45.0},
    {"id": 2, "nome": "Carbonara", "categoria": "massa", "preco": 52.0},
    {"id": 3, "nome": "Lasanha Bolonhesa", "categoria": "massa", "preco": 58.0},
    {"id": 4, "nome": "Tiramisù", "categoria": "sobremesa", "preco": 28.0},
    {"id": 5, "nome": "Quattro Stagioni", "categoria": "pizza", "preco": 49.0},
    {"id": 6, "nome": "Panna Cotta", "categoria": "sobremesa", "preco": 24.0},
]

@app.get("/pratos")
async def listar_pratos():
    return pratos