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
    # Busca o jogo no banco de dados
    jogo = db.query(Jogo).filter(Jogo.id == dados.jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Lista para armazenar os gols registrados
    gols_registrados = []

    # Processa cada jogador e a quantidade de gols
    for gol in dados.gols:
        jogador = db.query(Jogador).filter(Jogador.id == gol.jogador_id).first()
        if not jogador:
            raise HTTPException(status_code=404, detail=f"Jogador {gol.jogador_id} não encontrado")

        # Verifica se o jogador pertence a um dos times do jogo
        if jogador.id_time not in [jogo.time_casa_id, jogo.time_visitante_id]:
            raise HTTPException(
                status_code=400,
                detail=f"Jogador {jogador.nome} não pertence aos times deste jogo"
            )

        # Atualiza o placar do time correspondente
        if jogador.id_time == jogo.time_casa_id:
            jogo.placar_casa += gol.quantidade
        elif jogador.id_time == jogo.time_visitante_id:
            jogo.placar_visitante += gol.quantidade

        # Atualiza os dados do jogador e do time
        jogador.gols_realizados += gol.quantidade
        time = db.query(Time).filter(Time.id == jogador.id_time).first()
        time.gols_feitos += gol.quantidade

        # Atualiza os gols sofridos do time adversário
        time_adversario_id = (
            jogo.time_visitante_id if jogador.id_time == jogo.time_casa_id else jogo.time_casa_id
        )
        time_adversario = db.query(Time).filter(Time.id == time_adversario_id).first()
        time_adversario.gols_sofridos += gol.quantidade

        # Registra o gol no banco
        db.execute(
            gols_jogo.insert().values(
                jogo_id=jogo.id, jogador_id=gol.jogador_id, quantidade=gol.quantidade
            )
        )

        # Adiciona o gol registrado à lista
        gols_registrados.append({
            "jogador_id": gol.jogador_id,
            "quantidade": gol.quantidade
        })

    # Salva as alterações no banco de dados
    db.commit()
    db.refresh(jogo)

    # Retorna o jogo atualizado com os gols registrados
    return {
        "id": jogo.id,
        "time_casa_id": jogo.time_casa_id,
        "time_visitante_id": jogo.time_visitante_id,
        "data_hora": jogo.data_hora,
        "placar_casa": jogo.placar_casa,
        "placar_visitante": jogo.placar_visitante,
        "gols": gols_registrados
    }