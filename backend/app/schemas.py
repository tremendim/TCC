from pydantic import BaseModel

# Schemas para validação com Pydantic
class TimeCriar(BaseModel):
    nome: str
    divisao: str

class TimeResposta(BaseModel):
    id: int
    nome: str
    divisao: str

    class Config:
        orm_mode = True