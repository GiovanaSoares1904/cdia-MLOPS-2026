from pydantic import BaseModel, Field, field_validator
from typing import Optional

class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    descricao: Optional[str]
    disponivel: bool
    criado_em: str