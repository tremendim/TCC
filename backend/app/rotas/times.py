from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import Time
from schemas import TimeCriar, TimeResposta, ListaTimesResposta
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



@router.post("/", response_model=TimeResposta)
def criar_time(time: TimeCriar, db: Session = Depends(obter_sessao)):
    novo_time = Time(nome=time.nome, divisao=time.divisao)
    db.add(novo_time)
    db.commit()
    db.refresh(novo_time)
    return novo_time


@router.get("/", response_model=ListaTimesResposta)
def listar_times(db: Session = Depends(obter_sessao)):
    # Busca todos os times no banco de dados
    times = db.query(Time).all()
    
    # Retorna a quantidade total de times e a lista de times
    return {
        "total_times": len(times),  # Quantidade total de times
        "times": times  # Lista de times
    }


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
    db.delete(time)
    db.commit()
    return {"mensagem": "Time deletado com sucesso"}

#Configuração do Diretorio para salvar as imagens
IMAGENS_DIR = "imagens"
os.makedirs(IMAGENS_DIR, exist_ok=True)

@router.post("/{id_time}/upload-imagem")
def upload_imagem_time(
    id_time: int,
    imagem: UploadFile = File(...),
    db: Session = Depends(obter_sessao)
):
    # Verifica se o time existe
    time = db.query(Time).filter(Time.id == id_time).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    # Salva a imagem no diretório
    caminho_imagem = os.path.join(IMAGENS_DIR, f"time_{id_time}.jpg")
    with open(caminho_imagem, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    # Atualiza o caminho da imagem no banco de dados
    time.imagem = caminho_imagem
    db.commit()
    db.refresh(time)

    return {"mensagem": "Imagem do time atualizada com sucesso", "caminho_imagem": caminho_imagem}

@router.get("/{id_time}/imagem")
def obter_imagem_time(id_time: int, db: Session = Depends(obter_sessao)):
    # Busca o time no banco de dados
    time = db.query(Time).filter(Time.id == id_time).first()
    if not time or not time.imagem:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    # Retorna a imagem como uma resposta de arquivo
    return FileResponse(time.imagem)