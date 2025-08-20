FROM python:3.11-slim
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para mejor cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python con optimizaciones
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación completa
COPY . .

# Crear directorio de datos
RUN mkdir -p /app/data

# Configurar variables de entorno para PyTorch
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
ENV TOKENIZERS_PARALLELISM=false

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

