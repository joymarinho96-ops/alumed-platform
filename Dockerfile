FROM python:3.12-slim

# Dependencias del sistema
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

# Migrar base de datos y recopilar estáticos
RUN python manage.py collectstatic --noinput || true

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn alumed.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info"]
