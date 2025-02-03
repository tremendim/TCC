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
        "gols_realizados": jogador.gols_realizados  # Inclui os gols realizados
    }

#Listar jogadores de um time especifico
@router.get("/time/{id_time}", response_model=RespostaJogador)
def obter_jogador_time(id_time: int, db: Session = Depends(obter_sessao)):
    time = db.query(Time).filter(Time.id == id_time.first())
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return time.jogadores

# Configuração do diretório para salvar as imagens
IMAGENS_DIR = "imagens"
os.makedirs(IMAGENS_DIR, exist_ok=True)

@router.post("/{id_jogador}/upload-imagem")
def upload_imagem_jogador(
    id_jogador: int,
    imagem: UploadFile = File(...),
    db: Session = Depends(obter_sessao)
):
    # Verifica se o jogador existe
    jogador = db.query(Jogador).filter(Jogador.id == id_jogador).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    # Salva a imagem no diretório
    caminho_imagem = os.path.join(IMAGENS_DIR, f"jogador_{id_jogador}.jpg")
    with open(caminho_imagem, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    # Atualiza o caminho da imagem no banco de dados
    jogador.imagem = caminho_imagem
    db.commit()
    db.refresh(jogador)

    return {"mensagem": "Imagem do jogador atualizada com sucesso", "caminho_imagem": caminho_imagem}