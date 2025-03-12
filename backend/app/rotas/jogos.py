from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Jogo, Time,Jogador, gols_jogo
from schemas import JogoCriar, JogoResposta, AtualizarPlacarComGols

router = APIRouter()


@router.post("/", response_model=JogoResposta)
def criar_jogo(jogo: JogoCriar, db: Session = Depends(get_db)):
    # Verifica se os times existem
    time_casa = db.query(Time).filter(Time.id == jogo.time_casa_id).first()
    time_visitante = db.query(Time).filter(Time.id == jogo.time_visitante_id).first()
    if not time_casa or not time_visitante:
        raise HTTPException(status_code=404, detail="Um ou ambos os times não foram encontrados")

    novo_jogo = Jogo(
        time_casa_id=jogo.time_casa_id,
        time_visitante_id=jogo.time_visitante_id,
        data_hora=jogo.data_hora,
        placar_casa = 0,
        placar_visitante=0
    )
    db.add(novo_jogo)
    db.commit()
    db.refresh(novo_jogo)
    return novo_jogo

@router.get("/", response_model=List[JogoResposta])
def listar_jogos(db: Session = Depends(get_db)):
    jogos = db.query(Jogo).all()
    return jogos

@router.get("/{jogo_id}", response_model=JogoResposta)
def obter_jogo(jogo_id: int, db: Session = Depends(get_db)):
    # Busca o jogo no banco de dados
    jogo = db.query(Jogo).filter(Jogo.id == jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Retorna o jogo sem os detalhes dos gols
    return jogo


@router.put("/atualizar-placar", response_model=JogoResposta)
def atualizar_placar(dados: AtualizarPlacarComGols, db: Session = Depends(get_db)):
    jogo = db.query(Jogo).filter(Jogo.id == dados.jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Define o placar final
    jogo.placar_casa = dados.placar_casa
    jogo.placar_visitante = dados.placar_visitante

    # Define se o jogo foi finalizado baseado no argumento recebido
    jogo.jogo_finalizado = dados.jogo_finalizado

    # Obtém os times do jogo
    time_casa = db.query(Time).filter(Time.id == jogo.time_casa_id).first()
    time_visitante = db.query(Time).filter(Time.id == jogo.time_visitante_id).first()

    if not time_casa or not time_visitante:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    # Atualiza estatísticas de gols
    time_casa.gols_feitos += jogo.placar_casa
    time_casa.gols_sofridos += jogo.placar_visitante
    time_visitante.gols_feitos += jogo.placar_visitante
    time_visitante.gols_sofridos += jogo.placar_casa

    # Atualiza vitórias, derrotas, empates e pontuação
    if jogo.placar_casa > jogo.placar_visitante:
        time_casa.vitorias += 1
        time_casa.pontuacao += 3
        time_visitante.derrotas += 1
        jogo.time_ganhador = time_casa.id
        jogo.time_derrotado = time_visitante.id
    elif jogo.placar_casa < jogo.placar_visitante:
        time_visitante.vitorias += 1
        time_visitante.pontuacao += 3
        time_casa.derrotas += 1
        jogo.time_ganhador = time_visitante.id
        jogo.time_derrotado = time_casa.id
    else:  # Empate
        time_casa.empates += 1
        time_visitante.empates += 1
        time_casa.pontuacao += 1
        time_visitante.pontuacao += 1
        jogo.time_ganhador = None  # Sem vencedor
        jogo.time_derrotado = None  # Sem derrotado

    db.commit()
    db.refresh(jogo)

    return jogo