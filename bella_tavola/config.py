from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from typing import List, Optional
from functools import lru_cache

# --- CONFIGURAÇÕES (Settings) ---

class Settings(BaseSettings):
    app_name: str = "Bella Tavola API"
    debug: bool = False
    max_mesas: int = 20
    app_version: str = "1.0.0"
    app_description: str = "API do restaurante Bella Tavola"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()

# Instanciando para uso global (como solicitado no seu exemplo)
settings = get_settings()

# --- MODELOS E DADOS ---

class ReservaCreate(BaseModel):
    mesa: int
    nome: str
    pessoas: int
    
reservas = [
    {"id": 1, "mesa": 5, "nome": "Silva", "pessoas": 4, "ativa": True},
    {"id": 2, "mesa": 3, "nome": "Costa", "pessoas": 2, "ativa": False},
    {"id": 3, "mesa": 10, "nome": "Soares", "pessoas": 7, "ativa": True},
    {"id": 4, "mesa": 8, "nome": "Albuquerque", "pessoas": 3, "ativa": True},
    {"id": 5, "mesa": 20, "nome": "Braga", "pessoas": 5, "ativa": False},
    {"id": 6, "mesa": 24, "nome": "Oliveira", "pessoas": 10, "ativa": True},
]

# --- UTILITÁRIOS ---

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

# --- ROTAS (Router) ---
    
reservas_router = APIRouter(prefix="/reservas", tags=["Reservas"])

@reservas_router.get("/")
async def listar_reservas(apenas_ativas: bool = False):
    if apenas_ativas:
        return [r for r in reservas if r["ativa"]]
    return reservas

@reservas_router.post("/", status_code=201)
async def criar_reserva(reserva: ReservaCreate):
    # Regra de negócio usando o objeto settings global
    if reserva.mesa > settings.max_mesas:
        raise HTTPException(
            status_code=400,
            detail=f"Mesa inválida. O restaurante possui apenas {settings.max_mesas} mesas."
        )
    
    nova = {
        "id": len(reservas) + 1,
        "mesa": reserva.mesa,
        "nome": reserva.nome,
        "pessoas": reserva.pessoas,
        "ativa": True
    }
    reservas.append(nova)
    return nova

@reservas_router.delete("/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            r["ativa"] = False
            return {"mensagem": f"Reserva {reserva_id} cancelada com sucesso"}
    raise HTTPException(status_code=404, detail="Reserva não encontrada")

# --- APP PRINCIPAL ---

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    debug=settings.debug
)

app.include_router(reservas_router)

@app.get("/", tags=["Home"])
async def home():
    return {
        "app": settings.app_name,
        "config": {"max_mesas": settings.max_mesas},
        "resumo": {
            "total_reservas": len(reservas),
            "reservas_atuais": len([r for r in reservas if r["ativa"]])
        }
    }

# --- HANDLERS DE EXCEÇÃO ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return erro_padrao(request, 422, "Erro de validação nos dados enviados", exc.errors())

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return erro_padrao(request, exc.status_code, exc.detail, [])

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return erro_padrao(request, 500, "Erro interno do servidor", [str(exc)])