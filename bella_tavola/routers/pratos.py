from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from model_ex02_4_5 import CATEGORIAS_VALIDAS



router = APIRouter()

pratos = [
    {"id": 1, "nome": "Calabresa", "categoria": "pizza", "preco": 45.0, "disponivel": True},
    {"id": 2, "nome": "Fettuccine ao Sugo", "categoria": "massa", "preco": 52.0, "disponivel": True},
    {"id": 3, "nome": "Nhoque (Ginocchi) ao Molho Branco", "categoria": "massa", "preco": 58.0, "disponivel": False},
    {"id": 4, "nome": "Cannoli", "categoria": "sobremesa", "preco": 28.0, "disponivel": False},
    {"id": 5, "nome": "Franco com Catupiry", "categoria": "pizza", "preco": 49.0, "disponivel": True},
    {"id": 6, "nome": "Palha Italiana", "categoria": "sobremesa", "preco": 24.0, "disponivel": True},
]

class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    preco_promocional: Optional[float] = Field(default=None, gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True
    
    @field_validator("preco_promocional")
    @classmethod
    def validar_preco_promocional(cls, v, info):
        if v is None:
            return v
        if "preco" not in info.data:
            return v

        preco_original = info.data["preco"]

        if v >= preco_original:
            raise ValueError("Preço promocional deve ser menor que o preço original")

        desconto = (preco_original - v) / preco_original
        if desconto > 0.5:
            raise ValueError("Desconto não pode ser maior que 50% do preço original")

        return v


class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    descricao: Optional[str]
    disponivel: bool
    criado_em: str
    

@router.get("/")
async def home():
    return pratos

@router.get("/pratos")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False
):
    resultado = pratos
    
    if categoria:
        resultado = [p for p in resultado if p["categoria"].lower() == categoria.lower()]
    
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
        
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"] is True]
        
    return resultado


@router.get("/pratos/{prato_id}")
async def buscar_prato(prato_id: int, formato: str = "completo"):
    for prato in pratos:
        if prato["id"] == prato_id:
            if formato == "resumido":
                return {"nome": prato["nome"], "preco": prato["preco"]}
            return prato
        raise HTTPException(
            status_code=404,
            detail=f"Prato com id {prato_id} não encontrado"
        )

@router.get("/pratos/{prato_id}/detalhes")
async def detalhes_prato(prato_id: int, incluir_ingredientes: bool = False):
    for prato in pratos:
        if prato["id"] == prato_id:
            if incluir_ingredientes:
                return {**prato, "ingredientes": ["...lista..."]}
            return prato
    return {"mensagem": "Prato não encontrado"}
   

def formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}"

def formatar_lista(lista):
    return [{**item, "preco": formatar_preco(item["preco"])} for item in lista]




@router.post("/pratos/{prato_id}/aplicar_desconto")
async def aplicar_desconto(prato_id: int, percentual: float, dados: PratoInput):
    # Erro 404: recurso não existe
    prato = next((p for p in pratos if p["id"] == prato_id), None)
    if not prato:
        raise HTTPException(status_code=400, detail="Prato não encontrado")

    # Erro 400: dado válido estruturalmente, mas inválido para o negócio
    if percentual <= 0 or percentual > 50:
        raise HTTPException(
            status_code=400,
            detail="Percentual de desconto deve estar entre 1% e 50%"
        )

    # Erro 400: estado atual impede a operação
    print(f"Disponibilidade do prato: {prato['disponivel']}") # Debug
    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível aplicar desconto em prato indisponível"
        )

    prato["preco"] = prato["preco"] * (1 - percentual / 100)
    return prato

@router.post("/pratos", response_model=PratoOutput)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1 if pratos else 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump()
    }
    pratos.append(novo_prato)
    return novo_prato

class DisponibilidadeInput(BaseModel):
    disponivel: bool
    

@router.get("/pratos")
async def listar_pratos(categoria: Optional[str] = None):
    resultado = pratos

    if categoria:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise HTTPException(status_code=400, detail="Categoria inválida")
        resultado = [p for p in pratos if p["categoria"] == categoria.lower()]

    return formatar_lista(resultado)


@router.put("/pratos/{prato_id}/disponibilidade")
async def atualizar_disponibilidade(prato_id: int, disponivel: bool):
    prato = next((p for p in pratos if p["id"] == prato_id), None)

    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    if prato["disponivel"] == disponivel:
        estado = "disponível" if disponivel else "indisponível"
        raise HTTPException(
            status_code=400, 
            detail=f"O prato já está marcado como {estado}."
        )

    prato["disponivel"] = disponivel

    return {
        "mensagem": "Disponibilidade atualizada com sucesso",
        "prato": {**prato, "preco": formatar_preco(prato["preco"])}
    }
    







