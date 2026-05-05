from pydantic import BaseModel, Field, field_validator
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, PositiveInt
from typing import List


router = APIRouter()

reservas = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False},
    {"id": 3, "mesa": 10, "nome": "Soares", "pessoas": 7, "ativa": True},
    {"id": 4, "mesa": 8, "nome": "Albuquerque", "pessoas": 3, "ativa": True},
    {"id": 5, "mesa": 20, "nome": "Braga", "pessoas": 5, "ativa": False},
    {"id": 6, "mesa": 24, "nome": "Oliveira", "pessoas": 10, "ativa": True},
]

class ReservasInput(BaseModel):
    mesa: PositiveInt = Field(..., description="Número da mesa deve ser positivo")
    nome: str = Field(..., min_length=1)
    pessoas: PositiveInt = Field(..., description="Quantidade de pessoas deve ser positiva")


class ReservasOutput(BaseModel):
    id: int
    mesa: int
    nome: str
    pessoas: int
    ativa: bool

@router.get("/")
async def home():
    return {"mensagem": "API Bella Tavola funcionando"}

@router.get("/reservas", response_model=List[ReservasOutput])
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reservas if r["ativa"] is True]
    return reservas

@router.get("/reservas/{reserva_id}", response_model=ReservasOutput)
async def buscar_reserva(reserva_id: int):
    reserva = next((r for r in reservas if r["id"] == reserva_id), None)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva


@router.get("/mesa/{numero}")
async def reservas_por_mesa(numero: int):
    return [r for r in reservas if r["mesa"] == numero]

@router.post("/reservas", response_model=ReservasOutput, status_code=201)
async def criar_reserva(reserva: ReservasInput):
    # 3. Correção de Robustez: Geração de ID baseada no maior ID existente para evitar duplicatas
    novo_id = max([r["id"] for r in reservas], default=0) + 1
    
    nova = {
        "id": novo_id,
        **reserva.model_dump(),
        "ativa": True
    }
    reservas.append(nova)
    return nova

@router.delete("/reservas/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    reserva = next((r for r in reservas if r["id"] == reserva_id), None)
    
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    # 4. Correção de Robustez: Validação de estado (não cancelar o que já está inativo)
    if not reserva["ativa"]:
        return {"mensagem": "A reserva já se encontra inativa"}
        
    reserva["ativa"] = False
    return {"mensagem": "Reserva cancelada com sucesso"}

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
    
