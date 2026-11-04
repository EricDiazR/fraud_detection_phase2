# 1. Imagen base ligera con Python 3.10
FROM python:3.10-slim

# 2. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Variables de entorno para optimizar la salida de logs en consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Copiar e instalar las dependencias requeridas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código y el modelo de IA al contenedor
COPY . .

# 6. Exponer el puerto predeterminado de FastAPI
EXPOSE 8000

# 7. Comando principal para ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]