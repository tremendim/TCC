from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Jogo, Time
from schemas import JogoCriar, JogoResposta, AtualizarPlacar

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
        data_hora=jogo.data_hora
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
    jogo = db.query(Jogo).filter(Jogo.id == jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    return jogo



@router.put("/", response_model=JogoResposta)
def atualizar_placar(placar: AtualizarPlacar, db: Session = Depends(get_db)):
    # Busca o jogo pelo ID fornecido
    jogo = db.query(Jogo).filter(Jogo.id == placar.id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    
    # Atualiza os valores do placar
    jogo.placar_casa = placar.placar_casa
    jogo.placar_visitante = placar.placar_visitante
    db.commit()
    db.refresh(jogo)
    return jogo
