from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Schema para criar um time
class TimeCriar(BaseModel):
    nome: str
    divisao: str
    #Atende a RN02
    sigla: str = Field(..., min_length=3, max_length=4)


class RespostaJogador(BaseModel):
    id: int
    nome: str
    idade: int
    id_time: int
    posicao: str
    gols_realizados: int = 0
    cartoes_amarelos: int  
    cartoes_vermelhos: int  
    imagem: Optional[str] = None

    class Config:
        orm_mode = True


class TimeResposta(BaseModel):
    id: int
    nome: str
    divisao: str
    gols_feitos: int = 0
    gols_sofridos: int = 0
    sigla: Optional[str] = None
    imagem: Optional[str] = None
    vitorias: int
    derrotas: int
    empates: int
    pontuacao: int
    jogadores: List[RespostaJogador] = []  # Referência ao schema RespostaJogador

    class Config:
        orm_mode = True
class ListaTimesResposta(BaseModel):
    total_times: int  
    times: List[TimeResposta]  

    class Config:
        orm_mode = True


TimeResposta.update_forward_refs()

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
    imagem: Optional[str]
    cartoes_amarelos: Optional[int]
    cartoes_vermelhos: Optional[int]

class GolsJogo(BaseModel):
    jogador_id: int
    time_id: int
    quantidade: int

class JogoBase(BaseModel):
    time_casa_id: int
    time_visitante_id: int
    data_hora: datetime

class JogoCriar(JogoBase):
    time_casa_id: int
    time_visitante_id: int
    data_hora: datetime

class JogoResposta(BaseModel):
    id: int
    time_casa_id: int  
    time_casa: str  
    imagem_time_casa: Optional[str]  

    time_visitante_id: int  
    time_visitante: str  
    imagem_time_visitante: Optional[str]  

    data_hora: datetime
    placar_casa: Optional[int] = None
    placar_visitante: Optional[int] = None
    time_ganhador: Optional[str] = None  
    time_derrotado: Optional[str] = None  
    jogo_finalizado: bool

    class Config:
        orm_mode = True

class GolEntrada(BaseModel):
    jogador_id: int
    quantidade: int

class GolDetalhado(BaseModel):
    jogador_id: int
    jogador_nome: str
    time_sigla: str
    quantidade: int

class JogoDetalhado(BaseModel):
    id: int
    time_casa_id: int
    time_casa: str
    imagem_time_casa: Optional[str]
    time_visitante_id: int
    time_visitante: str
    imagem_time_visitante: Optional[str]
    data_hora: datetime
    placar_casa: Optional[int] = None
    placar_visitante: Optional[int] = None
    time_ganhador: Optional[str] = None
    time_derrotado: Optional[str] = None
    jogo_finalizado: bool
    gols: List[GolDetalhado]  
    jogadores_participantes: List[RespostaJogador]=[]

    class Config:
        orm_mode = True

class AtualizarPlacarComGols(BaseModel):
    jogo_id: int
    gols: List[GolEntrada]
    placar_casa: int
    placar_visitante: int
    jogo_finalizado: Optional[bool] = False