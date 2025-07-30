from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_consulta_endpoint():
    payload = {"pergunta": "Quais são as leis sobre agricultura?"}
    response = client.post("/consulta", json=payload)

    assert response.status_code == 200
    json_data = response.json()

    assert "resultados" in json_data
    assert isinstance(json_data["resultados"], list)
    assert len(json_data["resultados"]) > 0
