from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_consulta_endpoint():
    payload = {"pergunta": "Quais são as leis sobre agricultura?"}
    response = client.post("/consulta", json=payload)

    assert response.status_code == 200
    json_data = response.json()

    assert "resposta" in json_data
    assert isinstance(json_data["resposta"], str)
    assert len(json_data["resposta"]) > 0
    
    assert "leis_relacionadas" in json_data
    assert isinstance(json_data["leis_relacionadas"], list)
