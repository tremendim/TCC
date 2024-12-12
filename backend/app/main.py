from fastapi import FastAPI
from rotas import times

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="Campeonato de Futsal",
    description="API para gerenciar times, jogadores e partidas de um campeonato de Futsal.",
    version="1.0.0"
)

# Incluindo as rotas dos times
app.include_router(times.router, prefix="/times", tags=["Times"])

# Rota inicial
@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo ao sistema de acompanhamento do campeonato de Futsal!"}
