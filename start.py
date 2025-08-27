#!/usr/bin/env python
import subprocess
import time
import os
import signal
import sys

def signal_handler(sig, frame):
    print("\nParando os serviços...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Obtém a porta do ambiente (Railway define automaticamente)
    port = int(os.environ.get("PORT", 8000))
    
    # Detecta se está no Railway ou ambiente de produção
    is_production = (
        "RAILWAY_ENVIRONMENT" in os.environ or 
        "RAILWAY_PROJECT_ID" in os.environ or
        "RAILWAY_SERVICE_ID" in os.environ or
        "DYNO" in os.environ  # Heroku
    )
    
    if is_production:
        # Em produção, roda apenas o FastAPI
        print(f"Modo produção detectado - porta: {port}")
        os.environ["STREAMLIT_URL"] = f"https://your-app.railway.app/streamlit"
        
        print("Iniciando FastAPI em produção...")
        # Usa uvicorn diretamente para melhor controle
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--workers", "1"
        ])
    else:
        # Em desenvolvimento local, rodamos ambos separadamente
        print("Modo desenvolvimento local detectado")
        os.environ["STREAMLIT_URL"] = "http://localhost:8501"
        
        print("Iniciando FastAPI...")
        fastapi_process = subprocess.Popen([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--reload"
        ])
        
        print("Aguardando 5 segundos para o FastAPI inicializar...")
        time.sleep(5)
        
        print("Iniciando Streamlit...")
        streamlit_process = subprocess.Popen([
            "streamlit", "run", "tabela_generator/web_interface.py", 
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
        print("Ambos os serviços foram iniciados!")
        print(f"FastAPI: http://localhost:{port}")
        print("Streamlit: http://localhost:8501")
        print(f"Acesse o Streamlit via FastAPI em: http://localhost:{port}/gerador-tabelas")
        
        try:
            fastapi_process.wait()
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\nParando os serviços...")
            fastapi_process.terminate()
            streamlit_process.terminate()