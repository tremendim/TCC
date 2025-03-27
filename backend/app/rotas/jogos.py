from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from models import Jogo, Time,Jogador, gols_jogo
from schemas import JogoCriar, JogoResposta, AtualizarPlacarComGols, JogoDetalhado
from datetime import date, timedelta

router = APIRouter()

#Rota responsavel para a criação de um jogo
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

#Rota /GET responsavel para listar os jogos
@router.get("/", response_model=List[JogoResposta])
def listar_jogos(
    db: Session = Depends(get_db),
    data: str = Query(None, description="Filtrar por data (YYYY-MM-DD)"),
    periodo: str = Query(None, description="Filtrar por período: hoje, semana, mes")
):
    query = db.query(Jogo).options(
        joinedload(Jogo.time_casa),
        joinedload(Jogo.time_visitante),
        joinedload(Jogo.vencedor),
        joinedload(Jogo.perdedor)
    )

    # Filtrar por data específica
    if data:
        query = query.filter(
            Jogo.data_hora >= f"{data} 00:00:00",
            Jogo.data_hora <= f"{data} 23:59:59"
        )

    # Filtrar por período (hoje, semana, mês)
    elif periodo:
        hoje = date.today()
        if periodo == "hoje":
            query = query.filter(Jogo.data_hora >= hoje, Jogo.data_hora < hoje + timedelta(days=1))
        elif periodo == "semana":
            inicio_semana = hoje - timedelta(days=hoje.weekday())  # Segunda-feira
            fim_semana = inicio_semana + timedelta(days=6)
            query = query.filter(Jogo.data_hora >= inicio_semana, Jogo.data_hora <= fim_semana)
        elif periodo == "mes":
            inicio_mes = hoje.replace(day=1)
            proximo_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
            query = query.filter(Jogo.data_hora >= inicio_mes, Jogo.data_hora < proximo_mes)

    jogos = query.all()

    # Retorno da resposta mantendo o formato original
    return [
        {
            "id": jogo.id,
            "time_casa_id": jogo.time_casa.id if jogo.time_casa else None,
            "time_casa": jogo.time_casa.sigla if jogo.time_casa else "Desconhecido",
            "imagem_time_casa": jogo.time_casa.imagem if jogo.time_casa else None,

            "time_visitante_id": jogo.time_visitante.id if jogo.time_visitante else None,
            "time_visitante": jogo.time_visitante.sigla if jogo.time_visitante else "Desconhecido",
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

#Rota /Get responsavel para listar um jogo especifico
@router.get("/{id}", response_model=JogoDetalhado)
def obter_jogo(id: int, db: Session = Depends(get_db)):
    jogo = (
        db.query(Jogo)
        .options(
            joinedload(Jogo.time_casa),
            joinedload(Jogo.time_visitante),
            joinedload(Jogo.vencedor),
            joinedload(Jogo.perdedor),
        )
        .filter(Jogo.id == id)
        .first()
    )

    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Buscar os gols do jogo
    gols = (
        db.query(Jogador.id, Jogador.nome, Jogador.id_time, gols_jogo.c.quantidade)
        .join(gols_jogo, Jogador.id == gols_jogo.c.jogador_id)
        .filter(gols_jogo.c.jogo_id == jogo.id)
        .all()
    )

    # Buscar a sigla do time corretamente no modelo `Time`
    gols_formatados = [
        {
            "jogador_id": gol[0],
            "jogador_nome": gol[1],
            "time_sigla": db.query(Time.sigla).filter(Time.id == gol[2]).scalar(),
            "quantidade": gol[3],
        }
        for gol in gols
    ]

    return {
        "id": jogo.id,
        "time_casa_id": jogo.time_casa.id if jogo.time_casa else None,
        "time_casa": jogo.time_casa.sigla if jogo.time_casa else "N/A",
        "imagem_time_casa": jogo.time_casa.imagem if jogo.time_casa else None,
        "time_visitante_id": jogo.time_visitante.id if jogo.time_visitante else None,
        "time_visitante": jogo.time_visitante.sigla if jogo.time_visitante else "N/A",
        "imagem_time_visitante": jogo.time_visitante.imagem if jogo.time_visitante else None,
        "data_hora": jogo.data_hora,
        "placar_casa": jogo.placar_casa,
        "placar_visitante": jogo.placar_visitante,
        "time_ganhador": jogo.vencedor.sigla if jogo.vencedor else None,
        "time_derrotado": jogo.perdedor.sigla if jogo.perdedor else None,
        "jogo_finalizado": jogo.jogo_finalizado,
        "gols": gols_formatados,
    }

#Rota /PUT responsavel por atualizar as informações de um jogo.
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


