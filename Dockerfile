# Imagen base de Python
FROM python:3.10-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no privilegiado
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/downloads && \
    chown -R appuser:appuser /app

# Establecer directorio de trabajo
WORKDIR /app

# Instalar ffmpeg, git y nodejs (necesario para yt-dlp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY --chown=appuser:appuser app/ /app/

# Cambiar a usuario no privilegiado
USER appuser

# Exponer puerto
EXPOSE 5038

# Variables de entorno por defecto
ENV FLASK_APP=src/app.py \
    FLASK_ENV=production \
    FILE_MAX_AGE_HOURS=1 \
    CLEANUP_INTERVAL_MINUTES=5

# Comando de inicio con gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:5038", "--workers", "2", "--threads", "4", "--timeout", "300", "--chdir", "src", "app:app"]
