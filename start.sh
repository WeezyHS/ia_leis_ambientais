#!/bin/bash

# Script para iniciar FastAPI e Streamlit simultaneamente
echo "Iniciando FastAPI..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT &

# Aguardar FastAPI inicializar
echo "Aguardando FastAPI inicializar..."
sleep 5

# Iniciar Streamlit
echo "Iniciando Streamlit..."
streamlit run tabela_generator/web_interface.py --server.port 8501 --server.address 0.0.0.0