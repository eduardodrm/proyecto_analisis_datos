FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY api ./api

EXPOSE 8000

CMD ["python", "api/results_api.py"]

