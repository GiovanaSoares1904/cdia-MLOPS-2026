from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, PositiveInt
from typing import List, Optional
from datetime import datetime

router = APIRouter()

reserva = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True, "data_hora": datetime.now()},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False, "data_hora": datetime.now()},
    {"id": 3, "mesa": 10, "nome": "Soares", "pessoas": 7, "ativa": True, "data_hora": datetime.now()},
    {"id": 4, "mesa": 8, "nome": "Albuquerque", "pessoas": 3, "ativa": True, "data_hora": datetime.now()},
    {"id": 5, "mesa": 20, "nome": "Braga", "pessoas": 5, "ativa": False, "data_hora": datetime.now()},
    {"id": 6, "mesa": 15, "nome": "Oliveira", "pessoas": 10, "ativa": True, "data_hora": datetime.now()},
]

# --- Schemas ---

class ReservaInput(BaseModel):
    mesa: int = Field(ge=1, le=20)
    nome: str = Field(min_length=2, max_length=100)
    pessoas: int = Field(ge=1, le=10)
    data_hora: datetime

class ReservaUpdate(BaseModel):
    mesa: Optional[int] = Field(None, ge=1, le=20)
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    pessoas: Optional[int] = Field(None, ge=1, le=10)
    data_hora: Optional[datetime] = None
    ativa: Optional[bool] = None

class ReservaOutput(BaseModel):
    id: int
    mesa: int
    nome: str
    pessoas: int
    data_hora: datetime
    ativa: bool

# --- Endpoints ---

@router.get("/")
async def home():
    return {"mensagem": "API Bella Tavola funcionando"}

@router.get("/reserva", response_model=List[ReservaOutput])
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reserva if r["ativa"] is True]
    return reserva

@router.get("/reserva/{reserva_id}", response_model=ReservaOutput)
async def buscar_reserva(reserva_id: int):
    item = next((r for r in reserva if r["id"] == reserva_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return item

@router.post("/reserva", response_model=ReservaOutput, status_code=201)
async def criar_reserva(dados: ReservaInput):
    # Gera novo ID baseado no maior ID existente
    novo_id = max([r["id"] for r in reserva], default=0) + 1
    
    nova_reserva = {
        "id": novo_id,
        **dados.model_dump(),
        "ativa": True
    }
    reserva.append(nova_reserva)
    return nova_reserva

@router.put("/reserva/{reserva_id}", response_model=ReservaOutput)
async def atualizar_reserva(reserva_id: int, dados_novos: ReservaUpdate):
    item = next((r for r in reserva if r["id"] == reserva_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Reserva não encontrada para atualização")

    # Atualiza apenas os campos enviados (exclude_unset ignora os Nones do schema)
    update_data = dados_novos.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        item[key] = value
    
    return item

@router.delete("/reserva/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    item = next((r for r in reserva if r["id"] == reserva_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    if not item["ativa"]:
        return {"mensagem": "A reserva já se encontra inativa"}
        
    item["ativa"] = False
    return {"mensagem": "Reserva cancelada com sucesso"}


# Helper de erro
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