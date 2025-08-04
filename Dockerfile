# Dockerfile para o app principal (FastAPI, por exemplo)
FROM python:3.11-slim

WORKDIR /app

# Instala as dependências
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

EXPOSE 8000

# Inicia o app com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
