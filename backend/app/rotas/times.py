from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Time, Jogo, Jogador
from schemas import TimeCriar, TimeResposta, ListaTimesResposta
from database import SessionLocal
from typing import List, Optional
from collections import defaultdict


# Criando o roteador
router = APIRouter()

# Dependência do banco de dados
def obter_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/", response_model=TimeResposta)
def criar_time(time: TimeCriar, db: Session = Depends(obter_sessao)):

    #RN01:Todo time cadastrado deve possuir um nome único
    #Validação se esse nome de time já está cadastrado
    time_existente = db.query(Time).filter(Time.nome == time.nome).first()
    if time_existente:
        raise HTTPException(status_code=400, detail="Este time já existe")


    novo_time = Time(nome=time.nome, divisao=time.divisao,sigla=time.sigla)
    db.add(novo_time)
    db.commit()
    db.refresh(novo_time)
    return novo_time


@router.get("/", response_model=List[TimeResposta])
def listar_times(
    db: Session = Depends(obter_sessao),
    nome: Optional[str] = Query(None, description="Filtrar pelo nome do time"),
    sigla: Optional[str] = Query(None, description="Filtrar pela sigla do time"),
    pontuacao_min: Optional[int] = Query(None, description="Pontuação mínima"),
    pontuacao_max: Optional[int] = Query(None, description="Pontuação máxima"),
    ordem: Optional[str] = Query(None, description="Ordenar por: pontuacao, vitorias, saldo_gols")
):
    query = db.query(Time)

    #plicando filtros
    if nome:
        query = query.filter(Time.nome.ilike(f"%{nome}%"))
    if sigla:
        query = query.filter(Time.sigla.ilike(f"%{sigla}%"))
    if pontuacao_min is not None:
        query = query.filter(Time.pontuacao >= pontuacao_min)
    if pontuacao_max is not None:
        query = query.filter(Time.pontuacao <= pontuacao_max)

    #Ordenação
    if ordem:
        if ordem == "pontuacao":
            query = query.order_by(desc(Time.pontuacao))
        elif ordem == "vitorias":
            query = query.order_by(desc(Time.vitorias))
        elif ordem == "saldo_gols":
            query = query.order_by(desc(Time.gols_feitos - Time.gols_sofridos))

    times = query.all()

    #Convertendo os objetos corretamente para TimeResposta
    return times

@router.get("/classificacao")
def classificacao_por_divisao(db: Session = Depends(obter_sessao)):
    times = db.query(Time).order_by(Time.divisao, Time.pontuacao.desc()).all()

    classificacao = defaultdict(list)
    for time in times:
        classificacao[time.divisao].append(time)

    return classificacao
@router.get("/all", response_model=List[TimeResposta])
def listar_timess(db: Session = Depends(obter_sessao)):
    times = db.query(Time).all()
    return times

@router.get("/{id_time}", response_model=TimeResposta)
def obter_time(id_time: int, db: Session = Depends(obter_sessao)):
    time = db.query(Time).filter(Time.id == id_time).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return time



@router.delete("/{id_time}")
def deletar_time(id_time: int, db: Session = Depends(obter_sessao)):
    time = db.query(Time).filter(Time.id == id_time).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    
    #RN03 Um time não pode ser excluído se houver algum jogo registrado com sua participação
    # Validação se o time já particiou de algum jogo o filtro passa por toda query jogos e valida se o time casa ID ou Visitante
    # é igual ao time deletado
    verifica_participacao = db.query(Jogo).filter(
        (Jogo.time_casa_id == id_time) | (Jogo.time_visitante_id == id_time)
    ).first()

    if verifica_participacao:
        raise HTTPException(status_code=400, detail="O time não pode ser excluído, pois já participou de jogos.")


    db.delete(time)
    db.commit()
    return {"mensagem": "Time deletado com sucesso"}


#Rota /GET responsavel para listar o historio de jogos de um time
@router.get("/{id}/jogos")
def obter_jogos_do_time(id: int, db: Session = Depends(obter_sessao)):
    jogos = (
        db.query(Jogo)
        .filter((Jogo.time_casa_id == id) | (Jogo.time_visitante_id == id))
        .all()
    )
    return jogos
