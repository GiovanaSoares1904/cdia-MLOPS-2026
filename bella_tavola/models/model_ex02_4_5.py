from pydantic import BaseModel, Field, field_validator
from typing import Optional
from fastapi import FastAPI, HTTPException
import uvicorn


app = FastAPI()

CATEGORIAS_VALIDAS = {"pizza", "massa", "sobremesa", "entrada", "salada"}
TIPOS_VALIDOS = {"vinho", "agua", "refrigerante", "suco", "cerveja"}

bebidas = [
    {"id": 1, "nome": "Garibaldi", "tipo": "vinho", "preco": 30.0, "alcoolica": True, "volume_ml": 100},
    {"id": 2, "nome": "Limonata", "tipo": "refrigerante", "preco": 10.0, "alcoolica": False, "volume_ml": 500},
    {"id": 3, "nome": "Suco Natural", "tipo": "suco", "preco": 15.0, "alcoolica": False, "volume_ml": 300},
    {"id": 4, "nome": "Cerveja Lager", "tipo": "cerveja", "preco": 12.0, "alcoolica": True, "volume_ml": 600},
    {"id": 5, "nome": "Água Mineral", "tipo": "agua", "preco": 5.0, "alcoolica": False, "volume_ml": 500},
]

pratos = [
    {"id": 1, "nome": "Pizza Margherita", "categoria": "pizza", "preco": 40.0, "disponivel": True},
    {"id": 2, "nome": "Ravioli", "categoria": "massa", "preco": 35.0, "disponivel": True},
    {"id": 3, "nome": "Salada Caesar", "categoria": "salada", "preco": 25.0, "disponivel": True},
    {"id": 4, "nome": "Bruschetta", "categoria": "entrada", "preco": 20.0, "disponivel": True},
    {"id": 5, "nome": "Gelato", "categoria": "sobremesa", "preco": 15.0, "disponivel": True},
]

class PedidoInput(BaseModel):
    prato_id: int
    quantidade: int = Field(gt=0)
    observacao: Optional[str] = None


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
        "mensagem": "API rodando em http://127.0.0.1:5000",
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


# POST pedido com body solicitado
@app.post("/pedido")
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)

    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    if not prato.get("disponivel", True):
        raise HTTPException(status_code=400, detail="Prato indisponível")

    return {
        "mensagem": "Pedido realizado com sucesso",
        "pedido": {
            "prato": prato["nome"],
            "quantidade": pedido.quantidade,
            "observacao": pedido.observacao
        },
        "bebidas_disponiveis": formatar_lista(bebidas),
        "pratos_disponiveis": formatar_lista(pratos)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)