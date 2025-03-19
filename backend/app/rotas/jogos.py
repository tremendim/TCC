from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
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
    jogos = (
        db.query(Jogo)
        .options(
            joinedload(Jogo.time_casa),  # Carrega o time da casa
            joinedload(Jogo.time_visitante),  # Carrega o time visitante
            joinedload(Jogo.vencedor),  # Carrega o time vencedor
            joinedload(Jogo.perdedor)  # Carrega o time perdedor
        )
        .all()
    )

    # Ajustar a saída para retornar os nomes dos times
    return [
        {
            "id": jogo.id,
            "time_casa": jogo.time_casa.nome if jogo.time_casa else "Desconhecido",
            "imagem_time_casa": jogo.time_casa.imagem if jogo.time_casa else None,
            "time_visitante": jogo.time_visitante.nome if jogo.time_visitante else "Desconhecido",
            "imagem_time_visitante": jogo.time_visitante.imagem if jogo.time_visitante else None,
            "data_hora": jogo.data_hora,
            "placar_casa": jogo.placar_casa,
            "placar_visitante": jogo.placar_visitante,
            "time_ganhador": jogo.vencedor.nome if jogo.vencedor else None,
            "time_derrotado": jogo.perdedor.nome if jogo.perdedor else None,
            "jogo_finalizado": jogo.jogo_finalizado,
        }
        for jogo in jogos
    ]

@router.get("/{jogo_id}", response_model=JogoResposta)
def obter_jogo(jogo_id: int, db: Session = Depends(get_db)):
    # Busca o jogo no banco de dados
    jogo = db.query(Jogo).filter(Jogo.id == jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Retorna o jogo sem os detalhes dos gols
    return jogo


@router.put("/atualizar-placar")
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

    # Limpa os gols anteriores do jogo (caso seja uma atualização)
    db.execute(gols_jogo.delete().where(gols_jogo.c.jogo_id == jogo.id))

    # Verifica se há gols antes de processar
    if dados.gols:
        for gol in dados.gols:
            jogador = db.query(Jogador).filter(Jogador.id == gol.jogador_id).first()
            if not jogador:
                raise HTTPException(status_code=404, detail=f"Jogador {gol.jogador_id} não encontrado")

            # Adiciona os gols na tabela intermediária
            db.execute(gols_jogo.insert().values(
                jogo_id=jogo.id,
                jogador_id=gol.jogador_id,
                quantidade=gol.quantidade
            ))

            # Atualiza os gols do jogador
            jogador.gols_realizados += gol.quantidade
            db.add(jogador)

    # Salva todas as mudanças no banco de dados
    db.commit()
    db.refresh(jogo)

    return jogo