import firebase_admin
from firebase_admin import credentials, storage
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Carrega as credenciais do Firebase a partir da variável de ambiente
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_credentials_json:
    raise ValueError("A variável de ambiente FIREBASE_CREDENTIALS_JSON não foi definida.")

cred_dict = json.loads(firebase_credentials_json)
cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "storageBucket": "copao-2af37.firebasestorage.app"  # Verifique se este valor está correto
    })

# Função para enviar imagens ao Firebase Storage
def upload_imagem_firebase(file, filename):
    """Faz upload de um arquivo para o Firebase Storage e retorna a URL pública."""
    bucket = storage.bucket()
    blob = bucket.blob(f"imagens/{filename}")  # Caminho dentro do Firebase Storage
    blob.upload_from_file(file)
    blob.make_public()  # Torna a imagem acessível publicamente
    return blob.public_url