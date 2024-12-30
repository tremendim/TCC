from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

# Modelo do banco de dados
class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    divisao = Column(String, index=True)
    #Rleção para acessar os jogadores de um time
    jogadores = relationship("Jogador", back_populates="time")

class Jogador(Base):
    __tablename__ = "jogadores"

    id = Column(Integer, primary_key=True, index=True)  # ID do jogador
    nome = Column(String, index=True, nullable=False)  # Nome do jogador
    idade = Column(Integer, nullable=False)  # Idade do jogador
    posicao = Column(String, nullable=False)  # Posição em campo (ex.: goleiro, atacante, etc.)
    id_time = Column(Integer, ForeignKey("times.id"))  # Relação com o time (chave estrangeira)

    # Relação para acessar o time do jogador
    time = relationship("Time", back_populates="jogadores")

class Jogo(Base):
    __tablename__ = "jogos"

    id = Column(Integer, primary_key=True, index=True)
    time_casa_id = Column(Integer, ForeignKey("times.id"))
    time_visitante_id = Column(Integer, ForeignKey("times.id"))
    data_hora = Column(DateTime)
    placar_casa = Column(Integer, nullable=True)
    placar_visitante = Column(Integer, nullable=True)
    
    # Relacionamentos com os times
    time_casa = relationship("Time", foreign_keys=[time_casa_id])
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id])