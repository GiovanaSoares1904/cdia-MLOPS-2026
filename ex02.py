from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    preco: float = Field(gt=0, description="Preço em reais")
    categoria: str = Field(pattern="^(pizza|massa|sobremesa)$")

@app.get("/pratos/{prato_id}")
async def buscar_prato(prato_id: int):
    for prato in pratos:
        if prato["id"] == prato_id:
            return prato
    raise HTTPException(
        status_code=404,
        detail=f"Prato com id {prato_id} não encontrado"
    )


@app.get("/pratos/{prato_id}")
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

@app.get("/bebidas/{bebida_id}")
async def buscar_bebida(bebida_id: int):
    for bebida in bebidas:
        if bebida["id"] == bebida_id:
            return bebida
    raise HTTPException(
        status_code=404,
        detail=f"Bebida com id {bebida_id} não encontrada"
    )

class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100, description="Nome do prato")
    categoria: str = Field(description="Categoria do prato")
    preco: float = Field(gt=0, description="Preço em reais, deve ser positivo")
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True


class BebidaInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    tipo: str = Field(pattern="^(vinho|agua|refrigerante|suco|cerveja)$")
    preco: float = Field(gt=0)
    alcoolica: bool
    volume_ml: int = Field(ge=50, le=2000)


class PratoInput(BaseModel):
    nome: str = Field(min_length=3)
    preco: float = Field(gt=0)
    preco_promocional: float = Field(gt=0)

    @field_validator("preco_promocional")
    @classmethod
    def preco_promocional_menor_que_preco(cls, v, info):
        if "preco" in info.data and v >= info.data["preco"]:
            raise ValueError("Preço promocional deve ser menor que o preço original")
        return v

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


@app.post("/pratos/{prato_id}/aplicar_desconto")
async def aplicar_desconto(prato_id: int, percentual: float):
    # Erro 404: recurso não existe
    prato = next((p for p in pratos if p["id"] == prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    # Erro 400: dado válido estruturalmente, mas inválido para o negócio
    if percentual <= 0 or percentual > 50:
        raise HTTPException(
            status_code=400,
            detail="Percentual de desconto deve estar entre 1% e 50%"
        )

    # Erro 400: estado atual impede a operação
    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível aplicar desconto em prato indisponível"
        )

    prato["preco"] = prato["preco"] * (1 - percentual / 100)
    return prato

pedidos = []

class PedidoInput(BaseModel):
    prato_id: int
    quantidade: int = Field(ge=1)
    observacao: Optional[str] = None

class PedidoOutput(BaseModel):
    id: int
    prato_id: int
    nome_prato: str
    quantidade: int
    valor_total: float
    observacao: Optional[str]

@app.post("/pedidos", response_model=PedidoOutput)
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)

    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail=f"O prato '{prato['nome']}' não está disponível no momento"
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados inválidos",
            "detalhes": exc.errors(),
            "path": str(request.url)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url)
        }
    
app = FastAPI()

reservas = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False},
]

class ReservaInput(BaseModel):
    mesa: int
    nome: str
    pessoas: int

@app.get("/reservas/{reserva_id}")
async def buscar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            return r
    return {"erro": "não encontrada"}          # problema?

@app.post("/reservas")
async def criar_reserva(reserva: ReservaInput):
    # problema?
    nova = {"id": len(reservas) + 1, **reserva.model_dump(), "ativa": True}
    reservas.append(nova)
    return nova

@app.delete("/reservas/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            r["ativa"] = False
            return {"mensagem": "cancelada"}
    # problema?

@app.get("/reservas")
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reservas if r["ativa"] == "true"]  # problema?
    return reservas
