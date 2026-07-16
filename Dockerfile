FROM python:3.11-slim

# Dependencias do sistema (lxml, psycopg2)
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo
COPY . .

# Coletar arquivos estaticos
RUN python manage.py collectstatic --noinput || true

# Usar shell format para $PORT funcionar
CMD gunicorn alumed.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
