from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base


# Tabela intermediária para registrar os gols marcados em cada jogo
gols_jogo = Table(
    "gols_jogo",
    Base.metadata,
    Column("jogo_id", Integer, ForeignKey("jogos.id"), primary_key=True),
    Column("jogador_id", Integer, ForeignKey("jogadores.id"), primary_key=True),
    Column("quantidade", Integer, nullable=False)  # Quantidade de gols do jogador no jogo
)


class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    sigla = Column(String(4),nullable=True)
    divisao = Column(String, index=True)
    gols_feitos = Column(Integer, default=0)  # Gols feitos pelo time
    gols_sofridos = Column(Integer, default=0)  # Gols sofridos pelo time
    vitorias = Column(Integer, default=0)
    derrotas = Column(Integer, default=0)
    empates = Column(Integer, default=0)
    pontuacao = Column(Integer, default=0)
    imagem = Column(String, nullable=True)  

    #Rleção para acessar os jogadores de um time
    jogadores = relationship("Jogador", back_populates="time")

class Jogador(Base):
    __tablename__ = "jogadores"

    id = Column(Integer, primary_key=True, index=True)  
    nome = Column(String, index=True, nullable=False) 
    idade = Column(Integer, nullable=False)  
    posicao = Column(String, nullable=False)  
    id_time = Column(Integer, ForeignKey("times.id"))  
    gols_realizados = Column(Integer, default=0)  
    imagem = Column(String, nullable=True)
    cartoes_amarelos = Column(Integer, default=0) 
    cartoes_vermelhos = Column(Integer, default=0)  

    #Relação para acessar o time do jogador
    time = relationship("Time", back_populates="jogadores")

class Jogo(Base):
    __tablename__ = "jogos"

    id = Column(Integer, primary_key=True, index=True)
    time_casa_id = Column(Integer, ForeignKey("times.id"))
    time_visitante_id = Column(Integer, ForeignKey("times.id"))
    data_hora = Column(DateTime)
    placar_casa = Column(Integer, nullable=True)
    placar_visitante = Column(Integer, nullable=True)
    time_ganhador = Column(Integer, ForeignKey("times.id"))
    time_derrotado = Column(Integer, ForeignKey("times.id"))
    jogo_finalizado = Column(Boolean, default=False)
    
    #Relacionamentos com os times
    time_casa = relationship("Time", foreign_keys=[time_casa_id])
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id])
    vencedor = relationship("Time", foreign_keys=[time_ganhador])
    perdedor = relationship("Time", foreign_keys=[time_derrotado])
    gols = relationship("Jogador", secondary=gols_jogo, backref="jogos") 