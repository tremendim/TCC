from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_criar_jogador():
    response = client.post(
        "/jogadores/",
        json={"nome": "João", "idade": 22, "posicao": "Atacante", "id_time": 1}
    )
    assert response.status_code == 201
    assert response.json()["nome"] == "João"

def test_listar_jogadores():
    response = client.get("/jogadores/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
