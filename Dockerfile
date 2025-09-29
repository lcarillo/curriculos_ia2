# 1️⃣ Base Python 3.11 slim
FROM python:3.11-slim

# 2️⃣ Diretório de trabalho
WORKDIR /app

# 3️⃣ Instalar dependências do sistema necessárias para blis, psycopg2 e outras
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copiar requirements e instalar Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copiar todo o código do projeto
COPY . .

# 6️⃣ Rodar migrações e coletar arquivos estáticos
RUN python manage.py migrate --no-input
RUN python manage.py collectstatic --noinput

# 7️⃣ Comando para iniciar a aplicação
CMD ["gunicorn", "curriculos_ia.wsgi:application", "--bind", "0.0.0.0:10000"]
