from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from models import Jogador, Time
from schemas import CriarJogador, AtualizarJogador, RespostaJogador
from database import SessionLocal
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
def listar_jogadores(db: Session = Depends(obter_sessao)):
     return db.query(Jogador).all()


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
