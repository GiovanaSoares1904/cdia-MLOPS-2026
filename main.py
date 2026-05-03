from pydantic import BaseModel, Field, field_validator
from typing import Optional
from fastapi import FastAPI, HTTPException
import uvicorn
from datetime import datetime 
from fastapi import FastAPI, Request, HTTPException
from model_ex02_4_5 import app, pratos, formatar_lista, CATEGORIAS_VALIDAS, TIPOS_VALIDOS, bebidas 
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, PositiveInt
from typing import List
from fastapi.responses import JSONResponse


@app.get("/pratos")
async def listar_pratos(categoria: Optional[str] = None):
    resultado = pratos

    if categoria:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise HTTPException(status_code=400, detail="Categoria inválida")
        resultado = [p for p in pratos if p["categoria"] == categoria.lower()]

    return formatar_lista(resultado)
app = FastAPI(
    title="Bella Tavola API",
    description="API do restaurante Bella Tavola",
    version="1.0.0"
    )

@app.get("/")
async def root():
    return {
        "restaurante": "Bella Tavola",
        "mensagem": "Bem-vindo à nossa API",
        "chef": "Marco Rossi",
        "cidade": "São Paulo",
        "especialidades": "Massas Artesanais"   
    }
    
    
pratos = [
    {"id": 1, "nome": "Calabresa", "categoria": "pizza", "preco": 45.0, "disponivel": True},
    {"id": 2, "nome": "Fettuccine ao Sugo", "categoria": "massa", "preco": 52.0, "disponivel": True},
    {"id": 3, "nome": "Nhoque (Ginocchi) ao Molho Branco", "categoria": "massa", "preco": 58.0, "disponivel": False},
    {"id": 4, "nome": "Cannoli", "categoria": "sobremesa", "preco": 28.0, "disponivel": False},
    {"id": 5, "nome": "Franco com Catupiry", "categoria": "pizza", "preco": 49.0, "disponivel": True},
    {"id": 6, "nome": "Palha Italiana", "categoria": "sobremesa", "preco": 24.0, "disponivel": True},
]

bebidas = [
    {"id": 1, "nome": "Garibaldi", "tipo": "vinho", "preco": 30.0, "alcoolica": True, "volume_ml": 100},
    {"id": 2, "nome": "Limonata", "tipo": "refrigerante", "preco": 10.0, "alcoolica": False, "volume_ml": 500},
    {"id": 3, "nome": "Suco Natural", "tipo": "suco", "preco": 15.0, "alcoolica": False, "volume_ml": 300},
    {"id": 4, "nome": "Cerveja Lager", "tipo": "cerveja", "preco": 12.0, "alcoolica": True, "volume_ml": 600},
    {"id": 5, "nome": "Água Mineral", "tipo": "agua", "preco": 5.0, "alcoolica": False, "volume_ml": 500},
]

@app.get("/")
async def home():
    return pratos

@app.get("/pratos")
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

@app.get("/pratos/{prato_id}/detalhes")
async def detalhes_prato(prato_id: int, incluir_ingredientes: bool = False):
    for prato in pratos:
        if prato["id"] == prato_id:
            if incluir_ingredientes:
                return {**prato, "ingredientes": ["...lista..."]}
            return prato
    return {"mensagem": "Prato não encontrado"}

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
    
def formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}"

def formatar_lista(lista):
    return [{**item, "preco": formatar_preco(item["preco"])} for item in lista]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Erro de validação de dados", "errors": exc.errors()},
    )

@app.post("/pratos/{prato_id}/aplicar_desconto")
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


class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    descricao: Optional[str]
    disponivel: bool
    criado_em: str

@app.post("/pratos", response_model=PratoOutput)
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
    
@app.get("/pratos")
async def listar_pratos(categoria: Optional[str] = None):
    resultado = pratos

    if categoria:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise HTTPException(status_code=400, detail="Categoria inválida")
        resultado = [p for p in pratos if p["categoria"] == categoria.lower()]

    return formatar_lista(resultado)

@app.get("/pratos")
async def listar_pratos(categoria: Optional[str] = None):
    resultado = pratos

    if categoria:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise HTTPException(status_code=400, detail="Categoria inválida")
        resultado = [p for p in pratos if p["categoria"] == categoria.lower()]

    return formatar_lista(resultado)

@app.put("/pratos/{prato_id}/disponibilidade")
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
    
    
class PedidosInput(BaseModel):
    prato_id: int
    quantidade: int
    observacao: str = None


class BebidaInput(BaseModel):
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


class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    categoria: str
    preco: float = Field(gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True

    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, v):
        if v.lower() not in CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoria inválida. Use: {CATEGORIAS_VALIDAS}")
        return v.lower()

def formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}"


def formatar_lista(lista):
    return [{**item, "preco": formatar_preco(item["preco"])} for item in lista]

# HOME com bebidas + pratos
@app.get("/")
async def home():
    return {
        "mensagem": "API executando",
        "bebidas": formatar_lista(bebidas),
        "pratos": formatar_lista(pratos),
    }


# CARDÁPIO COMPLETO
@app.get("/cardapio")
async def cardapio():
    return {
        "bebidas": formatar_lista(bebidas),
        "pratos": formatar_lista(pratos),
    }


@app.get("/bebidas")
async def listar_bebidas(tipo: Optional[str] = None):
    resultado = bebidas

    if tipo:
        if tipo.lower() not in TIPOS_VALIDOS:
            raise HTTPException(status_code=400, detail="Tipo inválido")
        resultado = [b for b in bebidas if b["tipo"] == tipo.lower()]

    return formatar_lista(resultado)


@app.get("/pratos")
async def listar_pratos(categoria: Optional[str] = None):
    resultado = pratos

    if categoria:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise HTTPException(status_code=400, detail="Categoria inválida")
        resultado = [p for p in pratos if p["categoria"] == categoria.lower()]

    return formatar_lista(resultado)


# PUT disponibilidade
@app.put("/pratos/{prato_id}/disponibilidade")
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


# POST para pedidos

@app.post("/pedidos", status_code=status.HTTP_201_CREATED)
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

reservas = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False},
    {"id": 3, "mesa": 10, "nome": "Soares", "pessoas": 7, "ativa": True},
    {"id": 4, "mesa": 8, "nome": "Albuquerque", "pessoas": 3, "ativa": True},
    {"id": 5, "mesa": 20, "nome": "Braga", "pessoas": 5, "ativa": False},
    {"id": 6, "mesa": 24, "nome": "Oliveira", "pessoas": 10, "ativa": True},
]

class ReservaInput(BaseModel):
    mesa: PositiveInt = Field(..., description="Número da mesa deve ser positivo")
    nome: str = Field(..., min_length=1)
    pessoas: PositiveInt = Field(..., description="Quantidade de pessoas deve ser positiva")

class ReservaOutput(BaseModel):
    id: int
    mesa: int
    nome: str
    pessoas: int
    ativa: bool

@app.get("/")
async def home():
    return {"mensagem": "API Bella Tavola funcionando"}

@app.get("/reservas", response_model=List[ReservaOutput])
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reservas if r["ativa"] is True]
    return reservas

@app.get("/reservas/{reserva_id}", response_model=ReservaOutput)
async def buscar_reserva(reserva_id: int):
    reserva = next((r for r in reservas if r["id"] == reserva_id), None)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva

@app.post("/reservas", response_model=ReservaOutput, status_code=201)
async def criar_reserva(reserva: ReservaInput):
    # 3. Correção de Robustez: Geração de ID baseada no maior ID existente para evitar duplicatas
    novo_id = max([r["id"] for r in reservas], default=0) + 1
    
    nova = {
        "id": novo_id,
        **reserva.model_dump(),
        "ativa": True
    }
    reservas.append(nova)
    return nova

@app.delete("/reservas/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    reserva = next((r for r in reservas if r["id"] == reserva_id), None)
    
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    # 4. Correção de Robustez: Validação de estado (não cancelar o que já está inativo)
    if not reserva["ativa"]:
        return {"mensagem": "A reserva já se encontra inativa"}
        
    reserva["ativa"] = False
    return {"mensagem": "Reserva cancelada com sucesso"}

# 5. Correção de Robustez: Handlers que evitam o vazamento de logs do sistema para o cliente
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return erro_padrao(request, 422, "Dados de entrada inválidos", exc.errors())

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return erro_padrao(request, exc.status_code, exc.detail, [])

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Em produção, ocultamos o detalhe do erro 'str(exc)' para evitar expor a estrutura do código
    return erro_padrao(request, 500, "Erro interno do servidor", [])
