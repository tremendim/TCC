from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
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
    gols_feitos: int = 0
    gols_sofridos: int = 0
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
    gols_realizados: int

    class Config:
        orm_mode = True  # Permite conversão automática de objetos ORM do SQLAlchemy


class AtualizarJogador(BaseModel):

    nome: Optional[str]
    idade: Optional[int]
    posicao: Optional[str]
    id_time: Optional[int]

class GolsJogo(BaseModel):
    jogador_id: int
    time_id: int  # ID do time que fez o gol
    quantidade: int

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
    #gols: List[GolsJogo]  # Lista de gols marcados no jogo

    class config:
        orm_mode = True

class GolDetalhado(BaseModel):
    jogador_id: int
    quantidade: int

class AtualizarPlacarComGols(BaseModel):
    jogo_id: int
    gols: List[GolDetalhado]  # Lista de jogadores e quantidade de gols
