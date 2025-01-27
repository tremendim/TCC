from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Time
from schemas import TimeCriar, TimeResposta, ListaTimesResposta
from database import SessionLocal


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
