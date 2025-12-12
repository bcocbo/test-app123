
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias desde builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código fuente
COPY . .

# Usuario no-root
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app /home/appuser/.local

USER appuser

# Agregar .local/bin al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python healthcheck.py || exit 1

# Comando de inicio
CMD ["python", "app.py"]



# Metadata común
LABEL app.name="tes-app-123"
LABEL app.environment="dev"
LABEL app.type="custom"

LABEL app.language="python"

