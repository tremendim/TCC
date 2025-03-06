from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Schema para criar um time
class TimeCriar(BaseModel):
    nome: str
    divisao: str
    sigla: str = Field(..., min_length=4, max_length=4)

# Schema para resposta de um jogador
class RespostaJogador(BaseModel):
    id: int
    nome: str
    idade: int
    posicao: str
    gols_realizados: int = 0
    imagem: Optional[str] = None

    class Config:
        orm_mode = True

# Schema para resposta de um time
class TimeResposta(BaseModel):
    id: int
    nome: str
    divisao: str
    gols_feitos: int = 0
    gols_sofridos: int = 0
    sigla: Optional[str] = None
    imagem: Optional[str] = None
    jogadores: List[RespostaJogador] = []  # Referência ao schema RespostaJogador

    class Config:
        orm_mode = True
class ListaTimesResposta(BaseModel):
    total_times: int  # Quantidade total de times
    times: List[TimeResposta]  # Lista de times

    class Config:
        orm_mode = True

# Atualiza as referências futuras
TimeResposta.update_forward_refs()

# Outros schemas...
class CriarJogador(BaseModel):
    nome: str
    idade: int
    posicao: str
    id_time: int

class AtualizarJogador(BaseModel):
    nome: Optional[str]
    idade: Optional[int]
    posicao: Optional[str]
    id_time: Optional[int]

class GolsJogo(BaseModel):
    jogador_id: int
    time_id: int
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

    class Config:
        orm_mode = True

class GolDetalhado(BaseModel):
    jogador_id: int
    quantidade: int

class AtualizarPlacarComGols(BaseModel):
    jogo_id: int
    gols: List[GolDetalhado]
    placar_casa: int
    placar_visitante: int