from fastapi import APIRouter
from routers import pratos
from pydantic_settings import BaseSettings
from fastapi import FastAPI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.get("/")       # responde em /pratos/
@router.get("/{id}")   # responde em /pratos/{id}

app.include_router(pratos.router, prefix="/pratos", tags=["Pratos"])


class Settings(BaseSettings):
    app_name: str = "Bella Tavola API"
    debug: bool = False
    max_mesas: int = 20

    class Config:
        env_file = ".env"

settings = Settings()

router = APIRouter()

pratos = [...]  # a lista de pratos fica aqui

@router.get("/")
async def listar_pratos(categoria: Optional[str] = None):
    ...

@router.get("/{prato_id}")
async def buscar_prato(prato_id: int):
    ...

app = FastAPI(title="Bella Tavola API")

app.include_router(
    pratos.router,
    prefix="/pratos",
    tags=["Pratos"]
)

router = APIRouter()

pratos = [
    {"id": 1, "nome": "Margherita", "categoria": "pizza", "preco": 45.0, "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 2, "nome": "Carbonara", "categoria": "massa", "preco": 52.0, "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
]

class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    disponivel: bool = True

class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    disponivel: bool
    criado_em: str

@router.get("/")
async def listar_pratos(categoria: Optional[str] = None, apenas_disponiveis: bool = False):
    resultado = pratos
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado

@router.get("/{prato_id}")
async def buscar_prato(prato_id: int):
    for prato in pratos:
        if prato["id"] == prato_id:
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")

@router.post("/", response_model=PratoOutput)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1
    novo_prato = {"id": novo_id, "criado_em": datetime.now().isoformat(), **prato.model_dump()}
    pratos.append(novo_prato)
    return novo_prato

app = FastAPI(title="Bella Tavola API", version="1.0.0")

app.include_router(pratos.router, prefix="/pratos", tags=["Pratos"])
