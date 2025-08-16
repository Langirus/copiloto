FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación completa
COPY . .

# Crear directorio de datos
RUN mkdir -p /app/data

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

