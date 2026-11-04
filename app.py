import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="API de Detección de Transacciones Fraudulentas",
    version="1.0",
    description="Servicio de inferencia en tiempo real para análisis de riesgo transaccional",
)

class TransactionData(BaseModel):
    monto_usd: float = Field(..., gt=0.0, description="Monto total de la transacción en USD")
    distancia_habitual_km: float = Field(..., ge=0.0, description="Distancia física estimada respecto a la ubicación habitual del cliente")
    intentos_fallidos_cvv: int = Field(..., ge=0, description="Número de intentos fallidos al ingresar el código CVV")

try:
    model = joblib.load("model.joblib")
except Exception:
    model = None

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "Motor de Inferencia Anti-Fraude E-Commerce",
        "version": "1.0"
    }

@app.post("/predict")
def predict(data: TransactionData):
    if not model:
        raise HTTPException(status_code=500, detail="El modelo de detección de fraude no está disponible.")

    features = np.array([[data.monto_usd, data.distancia_habitual_km, data.intentos_fallidos_cvv]])
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0].tolist()

    estado_transaccion = "Bloqueada / Alto Riesgo" if prediction == 1 else "Aprobada / Bajo Riesgo"

    return {
        "decision": estado_transaccion,
        "codigo_fraude": prediction,
        "probabilidad_legitima": round(probabilities[0], 4),
        "probabilidad_fraude": round(probabilities[1], 4),
    }