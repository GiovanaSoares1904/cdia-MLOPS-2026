from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, status
from routers import pratos

from model_ex02_4_5 import TIPOS_VALIDOS

router = APIRouter()

pedidos = [
    {"id": 1, "nome": "foccacia", "categoria": "massa", "preco": 10.0},
    {"id": 2, "nome": "camarao", "categoria": "risotto", "preco": 30.0},
    {"id": 3, "nome": "carne", "categoria": "parmigiana", "preco": 60.0},
    {"id": 4, "nome": "ravioli", "categoria": "massa", "preco": 45.0},
    {"id": 5, "nome": "gelato", "categoria": "sobremesa", "preco": 15.0},
    {"id": 6, "nome": "panettone", "categoria": "sobremesa", "preco": 35.0},
]

  
class PedidoInput(BaseModel):
    prato_id: int
    quantidade: int
    observacao: str = None


class PedidoOutput(BaseModel):
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


def formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}"

def formatar_lista(lista):
    return [{**item, "preco": formatar_preco(item["preco"])} for item in lista]

class PedidosInput(BaseModel):
    prato_id: int
    quantidade: int
    observacao: str = None
    
class PedidosOutput(BaseModel):
    prato_id: int
    quantidade: int
    observacao: str = None 
    criado_em: str

# POST para pedidos

@router.post("/pedidos", status_code=status.HTTP_201_CREATED)
async def criar_pedidos(pedidos: PedidosInput):
    # 1. Procura o prato na lista global
    prato = next((p for p in pratos if p["id"] == pedidos.prato_id), None)

    # 2. ERRO 404: Se o ID enviado não constar na lista 'pratos'
    # É aqui que o 404 é disparado manualmente
    if prato is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Prato não encontrado"
        )

    # 3. ERRO 400: Se o prato existe, mas está indisponível
    if not prato.get("disponivel", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Prato indisponível"
        )

    return {
        "mensagem": "Pedidos realizado com sucesso",
        "detalhes": {
            "prato": prato["nome"],
            "quantidade": pedidos.quantidade,
            "observacao": pedidos.observacao,
            "total": formatar_preco(prato["preco"] * pedidos.quantidade)
        }
    }
    

def erro_padrao(request: Request, status: int, mensagem: str, detalhes: list):
    return JSONResponse(
        status_code=status,
        content={
            "erro": mensagem,
            "status": status,
            "path": str(request.url),
            "detalhes": detalhes
        }
    )

