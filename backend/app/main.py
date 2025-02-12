from fastapi import FastAPI
from rotas import times, jogadores, jogos, upload


# Inicialização da aplicação FastAPI
app = FastAPI(
    title="Campeonato de Futsal",
    description="API para gerenciar times, jogadores e partidas de um campeonato de Futsal.",
    version="1.0.0"
)

# Incluindo as rotas dos times
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(times.router, prefix="/times", tags=["Times"])
app.include_router(jogadores.router, prefix="/jogadores", tags=["Jogador"])
app.include_router(jogos.router, prefix="/jogos", tags=["Jogos"])

# Rota inicial
@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo ao sistema de acompanhamento do campeonato de Futsal!"}
