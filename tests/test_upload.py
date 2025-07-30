from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_pdf():
    with open("tests/lei_4791-2025_76128 (TESTE).pdf", "rb") as f:
        response = client.post("/upload", files={"file": ("lei_4791-2025_76128 (TESTE).pdf", f, "application/pdf")})

    assert response.status_code == 200

    data = response.json()
    assert "quantidade_chunks" in data
    assert isinstance(data["quantidade_chunks"], int)
    assert data["quantidade_chunks"] > 0

    assert "primeiros_chunks" in data
    assert isinstance(data["primeiros_chunks"], list)
    assert len(data["primeiros_chunks"]) > 0
