# Dockerfile
FROM python:3.11-slim

# Evita prompts e acelera pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Diretório de trabalho
WORKDIR /app

# Dependências do sistema que costumam ser úteis (ajuste se precisar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copia requirements e instala
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do projeto
COPY . /app

# Cloud Run injeta a porta em $PORT
ENV PORT=8080

# Se usar variáveis de ambiente (OpenAI, Supabase), você setará no Cloud Run
# ENV OPENAI_API_KEY=...  # (defina no painel, não aqui!)

# Expõe porta (opcional para Cloud Run)
EXPOSE 8080

# Comando de inicialização
# Ajuste o módulo para o caminho real do main: "app.main:app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
