from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session
from models import Jogador, Time, gols_jogo
from schemas import CriarJogador, AtualizarJogador, RespostaJogador
from database import SessionLocal
from typing import List, Optional
from sqlalchemy import desc, asc
import shutil
import os

# Criando o roteador
router = APIRouter()

# Dependência do banco de dados
def obter_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RespostaJogador)
def criar_jogador(jogador: CriarJogador, db: Session = Depends(obter_sessao)):

    #RN04 Cada jogador deve esta vinculado a apenas um time
    #Validação se esse jogador já está cadastrado em algum outro time
    jogador_existente = db.query(Jogador).filter(Jogador.nome == jogador.nome).first()
    if jogador_existente:
        raise HTTPException(status_code=400, detail="Este jogador já está vinculado a um time.")
    
    #RN05: O nome do jogador não pode estar em branco
    if not jogador.nome.strip():
        raise HTTPException(status_code=400, detail="O nome do jogador não pode estar em branco.")

    
    novo_jogador = Jogador(
        nome=jogador.nome,
        idade=jogador.idade,
        posicao=jogador.posicao,
        id_time=jogador.id_time
        )
    db.add(novo_jogador)
    db.commit()
    db.refresh(novo_jogador)
    return novo_jogador


#Rota /jogadores (Para listar os jogadores)
@router.get("/", response_model=list[RespostaJogador])
def listar_jogadores(
    nome: Optional[str] = Query(None),
    idade_min: Optional[int] = Query(None),
    idade_max: Optional[int] = Query(None),
    posicao: Optional[str] = Query(None),
    ordenar_por: Optional[str] = Query(
        None,
        description="Ordenar por: gols, amarelos, vermelhos"
    ),
    db: Session = Depends(obter_sessao)
):
    query = db.query(Jogador)

    if nome:
        query = query.filter(Jogador.nome.ilike(f"%{nome}%"))

    if idade_min is not None:
        query = query.filter(Jogador.idade >= idade_min)

    if idade_max is not None:
        query = query.filter(Jogador.idade <= idade_max)

    if posicao:
        query = query.filter(Jogador.posicao.ilike(f"%{posicao}%"))

    # 🔁 Ordenação dinâmica
    if ordenar_por == "gols":
        query = query.order_by(desc(Jogador.gols_realizados))
    elif ordenar_por == "amarelos":
        query = query.order_by(desc(Jogador.cartoes_amarelos))
    elif ordenar_por == "vermelhos":
        query = query.order_by(desc(Jogador.cartoes_vermelhos))
    if ordenar_por == "golsAsc":
        query = query.order_by(asc(Jogador.gols_realizados))
    elif ordenar_por == "amarelosAsc":
        query = query.order_by(asc(Jogador.cartoes_amarelos))
    elif ordenar_por == "vermelhosAsc":
        query = query.order_by(asc(Jogador.cartoes_vermelhos))

    jogadores = query.all()
    return jogadores


#Buscar um jogador por ID
@router.get("/{id_jogador}", response_model=RespostaJogador)
def obter_jogador(id_jogador: int, db: Session = Depends(obter_sessao)):
    jogador = db.query(Jogador).filter(Jogador.id == id_jogador).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return {
        "id": jogador.id,
        "nome": jogador.nome,
        "idade": jogador.idade,
        "posicao": jogador.posicao,
        "gols_realizados": jogador.gols_realizados,  # Inclui os gols realizados
        "imagem": jogador.imagem
    }

#Listar jogadores de um time especifico
@router.get("/time/{id_time}", response_model=RespostaJogador)
def obter_jogador_time(id_time: int, db: Session = Depends(obter_sessao)):
    time = db.query(Time).filter(Time.id == id_time.first())
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return time.jogadores

@router.put("/{jogador_id}")
def atualizar_jogador(jogador_id: int,dados: AtualizarJogador,db: Session = Depends(obter_sessao)):
    jogador = db.query(Jogador).filter(Jogador.id == jogador_id).first()

    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    # Validação: time existe (se fornecido)
    if dados.id_time is not None:
        time = db.query(Time).filter(Time.id == dados.id_time).first()
        if not time:
            raise HTTPException(status_code=404, detail="Time informado não existe.")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(jogador, key, value)

    db.commit()
    db.refresh(jogador)

    return {"mensagem": "Jogador atualizado com sucesso!", "jogador": jogador.id}


@router.delete("/{jogador_id}")
def excluir_jogador(jogador_id: int, db: Session = Depends(obter_sessao)):
    jogador = db.query(Jogador).filter(Jogador.id == jogador_id).first()

    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    # 🔍 Verifica se o jogador participou de algum jogo
    participacao = db.query(gols_jogo).filter(gols_jogo.c.jogador_id == jogador_id).first()

    if participacao:
        raise HTTPException(
            status_code=400,
            detail="Jogador não pode ser excluído pois participou de um ou mais jogos."
        )

    db.delete(jogador)
    db.commit()

    return {"message": "Jogador excluído com sucesso."}

