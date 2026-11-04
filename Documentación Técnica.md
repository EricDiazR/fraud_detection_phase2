# Documentación Técnica de Despliegue
## Proyecto de Inteligencia Artificial: Sistema Inteligente de Detección de Transacciones Fraudulentas en Tiempo Real

---

### 1. Información General del Documento

| Componente | Descripción |
| :--- | :--- |
| **Nombre del proyecto** | Sistema Inteligente de Detección de Transacciones Fraudulentas en Tiempo Real |
| **Versión del documento** | 1.0 |
| **Fecha** | 03 de noviembre de 2026 |
| **Responsables técnicos** | Equipo de Ingeniería de Datos y Ciberseguridad FinTech |
| **Institución** | Plataforma de E-Commerce / Pasarela de Pagos (Caso de Estudio) |
| **Estado del proyecto** | Desplegado en entorno de producción mediante contenedores Docker |

---

### 2. Introducción

#### 2.1 Propósito del Documento
El presente documento tiene como propósito describir la arquitectura, el proceso de despliegue, los componentes operativos y las consideraciones técnicas del sistema de inteligencia artificial desarrollado para evaluar el riesgo de fraude en transacciones financieras digitales en tiempo real, conforme al marco conceptual establecido en la norma **ISO/IEC 23053:2022** (Framework for Artificial Intelligence Systems Using Machine Learning).

#### 2.2 Alcance
**El proyecto comprende:**
* El sistema de IA en su fase operativa.
* Los componentes de entrada de datos, el modelo de machine learning y el motor de inferencia exposed como API REST mediante FastAPI.
* El proceso de contenerización y empaquetamiento con Docker en entorno WSL2 / Linux.
* Operación, monitoreo continuo y pruebas funcionales/casos extremos.

**El proyecto no contempla:**
* El pipeline completo de extracción e ingeniería de características históricas (*feature store*).
* La integración directa con redes adquirentes o pasarelas bancarias externas.
* La optimización de infraestructura de hardware a nivel de red física.

---

### 3. Marco Normativo y Referencias
* **ISO/IEC 23053:2022** - Framework for Artificial Intelligence (AI) Systems Using Machine Learning (ML).
* **ISO/IEC 22989** - Artificial Intelligence Concepts and Terminology.
* **PCI-DSS** - Standard de Seguridad de Datos para la Industria de Tarjetas de Pago.
* Lineamientos institucionales de protección de datos financieros personales.

---

### 4. Visión General del Sistema de IA

#### 4.1 Objetivo del Sistema de IA
El sistema tiene como objetivo analizar solicitudes de transacción digital en tiempo real (milisegundos) y evaluar el riesgo de fraude con tarjeta no presente (CNP), previniendo pérdidas financieras por contracargos y protegiendo a la plataforma de e-commerce.

#### 4.2 Tipo de Sistema de IA
Sistema de IA basado en **machine learning supervisado**.
Modelo de clasificación binaria:
* **Transacción de Alto Riesgo / Fraudulenta (Bloqueada - `1`)**
* **Transacción de Bajo Riesgo / Legítima (Aprobada - `0`)**

#### 4.3 Actores Involucrados
* **Usuarios finales:** Analistas de mitigación de fraude y riesgo operativo.
* **Usuarios técnicos:** Desarrolladores Backend, Data Scientists e Ingenieros MLOps.
* **Operadores del sistema:** Equipo de Infraestructura / DevSecOps.

---

### 5. Arquitectura del Sistema de IA

#### 5.1 Descripción General de la Arquitectura
El sistema adopta una arquitectura desacoplada basada en microservicios. La pasarela de pago (*checkout*) envía los atributos cuantitativos de la transacción a un servicio API REST contenerizado, el cual ejecuta el modelo de inferencia en memoria y retorna el dictamen inmediatamente.

#### 5.2 Componentes del Sistema (Alineados a ISO/IEC 23053)

| Componente | Descripción |
| :--- | :--- |
| **Fuente de datos** | Pasarela de Pago / Checkout de E-Commerce |
| **Procesamiento de datos** | Validaciones numéricas y parsing de tipos mediante esquemas de Pydantic |
| **Modelo ML** | Clasificador Random Forest balanceado serializado en formato `.joblib` |
| **Motor de inferencia** | Servicio API REST asíncrono con FastAPI y Uvicorn en Python |
| **Interfaz** | Documentación y cliente de prueba interactivo OpenAPI (Swagger UI) |
| **Infraestructura** | Entorno de contenedores Docker desplegado sobre Linux / WSL2 |

---

### 6. Datos en el Entorno de Despliegue

#### 6.1 Tipos de Datos Utilizados y Ejemplos de Inferencia
El motor de inferencia evalúa tres características cuantitativas extraídas en tiempo real durante el proceso de compra.

La siguiente tabla presenta el conjunto de datos de prueba utilizado para evaluar el comportamiento del modelo:

| Monto (USD) | Distancia Habitual (km) | Intentos Fallidos CVV | Predicción | Dictamen y Explicación del Resultado |
| :---: | :---: | :---: | :---: | :--- |
| **$25.00** | 1.5 | 0 | **0 (Aprobada)** | Operación habitual del cliente $\rightarrow$ Bajo Riesgo. |
| **$1,200.00** | 850.0 | 3 | **1 (Bloqueada)** | Anomalía geográfica severa y reintentos repetidos de CVV $\rightarrow$ Alto Riesgo. |
| **$45.00** | 5.0 | 0 | **0 (Aprobada)** | Compra menor en ubicación cercana $\rightarrow$ Transacción Legítima. |
| **$3,500.00** | 1,200.0 | 4 | **1 (Bloqueada)** | Monto elevado combinado con desplazamiento atípico e intentos fallidos. |
| **$89.90** | 1.5 | 0 | **0 (Aprobada)** | Erogación cotidiana dentro de parámetros habituales. |
| **$4,800.00** | 3,000.0 | 5 | **1 (Bloqueada)** | Alerta crítica: monto alto, distancia internacional y fallos masivos de CVV. |

---

#### 6.2 Justificación de las Variables de Entrada y Variable Objetivo

##### A. Variables de Entrada (*Features*)
1. **Monto en USD (`monto_usd`):** 
   * **Tipo:** Numérico continuo ($\mathbb{R}^+$).
   * **Justificación:** Representa el impacto financiero directo. Las operaciones no autorizadas buscan procesar montos elevados antes del bloqueo de la tarjeta.
2. **Distancia Habitual en Kilómetros (`distancia_habitual_km`):** 
   * **Tipo:** Numérico continuo ($\mathbb{R}^+$).
   * **Justificación:** Mide la distancia física entre la ubicación del pago (IP/GPS) y el domicilio o área habitual del usuario. Desplazamientos atípicos sugieren suplantación.
3. **Intentos Fallidos de CVV (`intentos_fallidos_cvv`):** 
   * **Tipo:** Numérico discreto ($\mathbb{Z} \ge 0$).
   * **Justificación:** Evalúa la cantidad de errores al ingresar el código de seguridad. Conconteos elevados indican posibles ataques automatizados de fuerza bruta.

##### B. Variable Objetivo (*Target*)
* **Dictamen de Riesgo (`es_fraude` / `codigo_fraude`):**
  * **Tipo:** Clasificación Binaria ($\{0, 1\}$).
  * **Significado:** `0`: Transacción Aprobada / Bajo Riesgo; `1`: Transacción Bloqueada / Alto Riesgo.

---

#### 6.3 Reglas de Inferencia del Modelo ML

El modelo supervisado Random Forest evalúa la combinación de los tres atributos siguiendo las siguientes fronteras de decisión principales:

1. **Patrón de Fuerza Bruta:** 
   $$\text{Si } \text{intentos\_fallidos\_cvv} \ge 3 \implies \text{Predicción} = 1 \text{ (Bloqueada)}$$
2. **Patrón de Desplazamiento Anómalo con Monto Elevado:**
   $$\text{Si } \text{distancia\_habitual\_km} > 400 \text{ km} \quad \text{Y} \quad \text{monto\_usd} > \$1,000.00 \implies \text{Predicción} = 1 \text{ (Bloqueada)}$$
3. **Tráfico Legítimo Sin Fricción:**
   $$\text{Si } \text{intentos\_fallidos\_cvv} = 0 \quad \text{Y} \quad \text{distancia\_habitual\_km} \le 50 \text{ km} \implies \text{Predicción} = 0 \text{ (Aprobada)}$$

---

#### 6.4 Gestión y Gobierno de Datos
* **Validación de Entradas:** Los esquemas de Pydantic rechazan solicitudes con valores inválidos (por ejemplo, montos negativos) emitiendo respuestas HTTP `422 Unprocessable Entity`.
* **Seguridad PCI-DSS:** No se procesan ni almacenan números de tarjeta completos (PAN) ni datos personales identificables.
* **Cifrado en Transito:** La comunicación con el contenedor se realiza mediante HTTPS/TLS.

---

### 7. Modelo de Machine Learning en Producción

#### 7.1 Descripción del Modelo
* **Algoritmo:** Random Forest Classifier.
* **Entradas:** `monto_usd` (float), `distancia_habitual_km` (float), `intentos_fallidos_cvv` (int).
* **Salidas:** Dictamen de riesgo (`Aprobada / Bajo Riesgo` o `Bloqueada / Alto Riesgo`) y distribución de probabilidades.
* **Métrica Principal:** Exactitud (Accuracy): > 90%; ROC-AUC: 0.93.

#### 7.2 Ciclo de Vida del Modelo
* Entrenamiento offline y exportación del artefacto `model.joblib`.
* Pruebas de integración automatizadas con `pytest` previas a la producción.
* Reentrenamiento programado y sustitución del contenedor sin interrupción del servicio (*zero-downtime*).

---

### 8. Proceso de Despliegue del Sistema

#### 8.1 Estrategia de Despliegue
Implementación contenerizada mediante **Docker**, permitiendo aislamiento de dependencias, portabilidad y ejecuciones homogéneas tanto en entorno local (WSL2/Ubuntu) como en servicios Cloud PaaS (AWS ECS, Google Cloud Run o Azure Container Instances).

#### 8.2 Pipeline de Despliegue Paso a Paso
1. **Entrenamiento local:** Ejecución de `python train_model.py` para generar el binario `model.joblib`.
2. **Construcción de la Imagen:** Ejecución del comando de compilación de Docker:
   ```bash
   docker build -t detector-fraude-api:v1.0 .
