FROM python:3.12-slim

# No escribir archivos pyc y salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar requirements de producción e instalar (aprovecha cache de docker)
COPY requirements-prod.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# Copiar el resto del código
COPY . .

# Comando por defecto para producción: usa la variable PORT si está definida
CMD ["sh", "-c", "uvicorn src.application.api_app:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --workers 1"]