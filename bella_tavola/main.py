from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers import pratos, bebidas, pedidos, reservas
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

# --- Manipuladores de Exceção Personalizados ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detalhes = [
        {"campo": " -> ".join(str(loc) for loc in e["loc"]), "mensagem": e["msg"]} 
        for e in exc.errors()
    ]
    
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": detalhes
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Captura erros de regras de negócio (como reserva não encontrada).
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail, 
            "status": exc.status_code, 
            "path": str(request.url), 
            "detalhes": []
        }
    )

# --- Inclusão das Rotas ---

app.include_router(pratos.router,   prefix="/pratos",   tags=["Pratos"])
app.include_router(bebidas.router,  prefix="/bebidas",  tags=["Bebidas"])
app.include_router(pedidos.router,  prefix="/pedidos",  tags=["Pedidos"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])

# --- Rota Raiz ---

@app.get("/", tags=["Geral"])
async def root():
    return {
        "restaurante": settings.app_name, 
        "versao": settings.app_version,
        "limite_mesas": settings.max_mesas,
        "status": "API operacional"
    }