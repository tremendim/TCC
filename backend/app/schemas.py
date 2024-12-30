from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Schemas para validação com Pydantic

#Validação do metodo Post para criar times
class TimeCriar(BaseModel):
    nome: str
    divisao: str

#Validação da resposta do metodo Get do time
class TimeResposta(BaseModel):
    id: int
    nome: str
    divisao: str
    jogadores: List["RespostaJogador"] = []

    class Config:
        orm_mode = True

#Usado na rota de criação (POST), valida os dados enviados pelo cliente.
class CriarJogador(BaseModel):
    nome: str
    idade: int
    posicao: str
    id_time: int  # O time ao qual o jogador pertence (chave estrangeira)

#Define o formato dos dados que serão enviados pela API como resposta ao cliente.
class RespostaJogador(BaseModel):
    id: int
    nome: str
    idade: int
    posicao: str
 #   time: Optional[TimeResposta] #Inclui informações do time no retorno

    class Config:
        orm_mode = True  # Permite conversão automática de objetos ORM do SQLAlchemy


class AtualizarJogador(BaseModel):

    nome: Optional[str]
    idade: Optional[int]
    posicao: Optional[str]
    id_time: Optional[int]

class JogoBase(BaseModel):
    time_casa_id: int
    time_visitante_id: int
    data_hora: datetime

class JogoCriar(JogoBase):
    pass

class JogoResposta(JogoBase):
    id: int
    placar_casa: Optional[int] = None
    placar_visitante: Optional[int] = None

    class config:
        orm_mode = True

from pydantic import BaseModel

class AtualizarPlacar(BaseModel):
    id: int
    placar_casa: int
    placar_visitante: int
