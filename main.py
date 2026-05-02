from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import uvicorn
from datetime import datetime

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
    return {"mensagem": "Prato não encontrado"}


@app.get("/pratos/{prato_id}/detalhes")
async def detalhes_prato(prato_id: int, incluir_ingredientes: bool = False):
    for prato in pratos:
        if prato["id"] == prato_id:
            if incluir_ingredientes:
                return {**prato, "ingredientes": ["...lista..."]}
            return prato
    return {"mensagem": "Prato não encontrado"}

class PratoInput(BaseModel):
    nome: str
    categoria: str
    preco: float
    disponivel: bool = True 
    descricao: Optional[str] = None
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

bebidas = [
    {"id": 1, "nome": "Garibaldi", "tipo": "vinho", "preco": 30.0, "alcoolica": True, "volume_ml": 100},
    {"id": 2, "nome": "Limonata", "tipo": "refrigerante", "preco": 10.0, "alcoolica": False, "volume_ml": 500},
    {"id": 3, "nome": "Suco Natural", "tipo": "suco", "preco": 15.0, "alcoolica": False, "volume_ml": 300},
    {"id": 4, "nome": "Cerveja Lager", "tipo": "cerveja", "preco": 12.0, "alcoolica": True, "volume_ml": 600},
    {"id": 5, "nome": "Água Mineral", "tipo": "agua", "preco": 5.0, "alcoolica": False, "volume_ml": 500},
]
class BebidaInput(BaseModel):
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int

class BebidaOutput(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str

@app.get("/bebidas")
async def listar_bebidas(
    tipo: Optional[str] = None,
    alcoolica: Optional[bool] = None
):
    resultado = bebidas
    if tipo:
        resultado = [b for b in resultado if b["tipo"] == tipo]
    if alcoolica is not None:
        resultado = [b for b in resultado if b["alcoolica"] == alcoolica]
    return resultado

@app.get("/bebidas/{bebida_id}")
async def buscar_bebida(bebida_id: int):
    for bebida in bebidas:
        if bebida["id"] == bebida_id:
            return bebida
    return {"mensagem": "Bebida não encontrada"}

@app.post("/bebidas", response_model=BebidaOutput)
async def criar_bebida(bebida: BebidaInput):
    novo_id = max(b["id"] for b in bebidas) + 1
    nova_bebida = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **bebida.model_dump()
    }
    bebidas.append(nova_bebida)
    return nova_bebida
