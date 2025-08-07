#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar a interface web do gerador de tabelas
"""

import subprocess
import sys
from pathlib import Path

def executar_streamlit():
    """Executa a interface web usando Streamlit"""
    
    # Caminho para o arquivo da interface web
    interface_path = Path(__file__).parent / "tabela_generator" / "web_interface.py"
    
    print("🚀 Iniciando interface web do gerador de tabelas...")
    print("📊 IA Direcionada para Organização de Leis Ambientais")
    print("-" * 50)
    
    try:
        # Executar streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(interface_path)]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Interface web encerrada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao executar interface web: {e}")
        print("\n💡 Certifique-se de que o Streamlit está instalado:")
        print("   pip install streamlit")

if __name__ == "__main__":
    executar_streamlit()