from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_transaccion_legitima():
    payload = {"monto_usd": 25.0, "distancia_habitual_km": 1.5, "intentos_fallidos_cvv": 0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "Aprobada / Bajo Riesgo"

def test_transaccion_sospechosa():
    payload = {"monto_usd": 4500.0, "distancia_habitual_km": 1500.0, "intentos_fallidos_cvv": 4}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "Bloqueada / Alto Riesgo"

def test_caso_extremo_monto_invalido():
    # Monto negativo o cero (violación de rango validado)
    payload = {"monto_usd": -50.0, "distancia_habitual_km": 0.0, "intentos_fallidos_cvv": 0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422