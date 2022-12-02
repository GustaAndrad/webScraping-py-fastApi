from pydantic import BaseModel


class RespostaHealthCheck(BaseModel):
    status: int
    descricao: str


class EntradaDetranMG(BaseModel):
    placa: str
    chassi: str
