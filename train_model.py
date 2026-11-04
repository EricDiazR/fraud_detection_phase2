import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Datos sintéticos de transacciones financieras
# Variables: monto_usd, distancia_habitual_km, intentos_fallidos_cvv, hora_transaccion (0-23)
data = {
    "monto_usd": [15.5, 1200.0, 45.0, 3500.0, 89.9, 1500.0, 25.0, 4800.0, 60.0, 15.0],
    "distancia_habitual_km": [2.0, 850.0, 5.0, 1200.0, 1.5, 450.0, 10.0, 3000.0, 3.0, 1.0],
    "intentos_fallidos_cvv": [0, 3, 0, 4, 0, 2, 0, 5, 0, 0],
    "es_fraude": [0, 1, 0, 1, 0, 1, 0, 1, 0, 0]  # 0: Legítima, 1: Fraudulenta
}

df = pd.DataFrame(data)
X = df[["monto_usd", "distancia_habitual_km", "intentos_fallidos_cvv"]]
y = df["es_fraude"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modelo basado en Random Forest para clasificación de riesgo de transacción
model = RandomForestClassifier(n_estimators=15, random_state=42)
model.fit(X_train, y_train)

# Guardar artefacto del modelo
joblib.dump(model, "model.joblib")
print("Modelo de Detección de Fraude guardado en model.joblib")