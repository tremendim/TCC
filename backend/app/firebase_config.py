import firebase_admin
from firebase_admin import credentials, storage
import os

# Caminho do arquivo JSON da chave privada
FIREBASE_CREDENTIALS = "firebase-adminsdk.json"

# Inicializa o Firebase se ainda não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
        "storageBucket": "copao-2af37.firebasestorage.app"
    })

# Função para enviar imagens ao Firebase Storage
def upload_imagem_firebase(file, filename):
    """Faz upload de um arquivo para o Firebase Storage e retorna a URL pública."""
    bucket = storage.bucket()
    blob = bucket.blob(f"imagens/{filename}")  # Caminho dentro do Firebase Storage
    blob.upload_from_file(file)
    blob.make_public()  # Torna a imagem acessível publicamente
    return blob.public_url