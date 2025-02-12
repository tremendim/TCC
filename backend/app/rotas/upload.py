from fastapi import APIRouter, UploadFile, File, HTTPException
from firebase_config import upload_imagem_firebase
from database import SessionLocal
from models import Jogador, Time

router = APIRouter()  # Certifique-se de que o APIRouter foi criado corretamente

@router.post("/", tags=["Upload"])
async def upload_imagem(tipo: str, id: int, file: UploadFile = File(...)):
    """
    Upload de imagem para jogador ou time, armazenando no Firebase.
    """
    if tipo not in ["jogador", "time"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'jogador' ou 'time'.")

    extensao = file.filename.split(".")[-1].lower()
    if extensao not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Apenas arquivos PNG, JPG e JPEG são permitidos.")

    filename = f"{tipo}_{id}.{extensao}"
    url_imagem = upload_imagem_firebase(file.file, filename)

    db = SessionLocal()
    if tipo == "jogador":
        jogador = db.query(Jogador).filter(Jogador.id == id).first()
        if not jogador:
            raise HTTPException(status_code=404, detail="Jogador não encontrado")
        jogador.imagem = url_imagem
    elif tipo == "time":
        time = db.query(Time).filter(Time.id == id).first()
        if not time:
            raise HTTPException(status_code=404, detail="Time não encontrado")
        time.imagem = url_imagem

    db.commit()
    db.close()

    return {"mensagem": "Upload realizado com sucesso", "url": url_imagem}
