from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Lista de tipos permitidos
TIPOS_VALIDOS = ["vinho", "refrigerante", "suco", "cerveja", "agua"]

router = APIRouter()

# Mock de dados inicial
bebidas = [
    {"id": 1, "nome": "Garibaldi", "tipo": "vinho", "preco": 30.0, "alcoolica": True, "volume_ml": 100, "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    {"id": 2, "nome": "Limonata", "tipo": "refrigerante", "preco": 10.0, "alcoolica": False, "volume_ml": 500, "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    {"id": 3, "nome": "Suco Natural", "tipo": "suco", "preco": 15.0, "alcoolica": False, "volume_ml": 300, "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    {"id": 4, "nome": "Cerveja Lager", "tipo": "cerveja", "preco": 12.0, "alcoolica": True, "volume_ml": 600, "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    {"id": 5, "nome": "Água Mineral", "tipo": "agua", "preco": 5.0, "alcoolica": False, "volume_ml": 500, "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
]

# Funções Auxiliares
def formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}"

def formatar_lista(lista):
    return [{**item, "preco": formatar_preco(item["preco"])} for item in lista]

# Schemas Pydantic
class BebidasInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    tipo: str
    preco: float = Field(gt=0)
    alcoolica: bool
    volume_ml: int = Field(ge=50, le=2000)

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v):
        if v.lower() not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Use: {TIPOS_VALIDOS}")
        return v.lower()

class BebidasOutput(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str

# Endpoints
@router.get("/")
async def home():
    return {
        "mensagem": "API de Bebidas executando",
        "bebidas": formatar_lista(bebidas),
    }

@router.get("/cardapio")
async def cardapio():
    return {
        "bebida": formatar_lista(bebidas),
    }

@router.get("/bebidas")
async def listar_bebidas(tipo: Optional[str] = None):
    resultado = bebidas

    if tipo:
        if tipo.lower() not in TIPOS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"Tipo inválido. Opções: {TIPOS_VALIDOS}")
        resultado = [b for b in bebidas if b["tipo"] == tipo.lower()]

    return formatar_lista(resultado)
    