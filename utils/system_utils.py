#!/usr/bin/env python3
"""
Utilitários do Sistema - Configuração e Manutenção
Inclui funções para instalação do Selenium e limpeza do Pinecone
"""

import subprocess
import sys
import os
import requests
import zipfile
from pathlib import Path
from pinecone import Pinecone

# ==================== INSTALAÇÃO SELENIUM ====================

def install_package(package):
    """Instala um pacote Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package}: {e}")
        return False

def download_edge_driver():
    """Baixa o Microsoft Edge WebDriver"""
    try:
        driver_url = "https://msedgedriver.azureedge.net/LATEST_STABLE/edgedriver_win64.zip"
        
        print("📥 Baixando Microsoft Edge WebDriver...")
        response = requests.get(driver_url)
        
        if response.status_code == 200:
            zip_path = "edgedriver.zip"
            with open(zip_path, "wb") as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            os.remove(zip_path)
            print("✅ Edge WebDriver baixado e extraído")
            return True
        else:
            print(f"❌ Erro ao baixar EdgeDriver: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao baixar EdgeDriver: {e}")
        return False

def check_edge_installation():
    """Verifica se o Microsoft Edge está instalado"""
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    for path in edge_paths:
        if os.path.exists(path):
            print(f"✅ Microsoft Edge encontrado em: {path}")
            return True
    
    print("❌ Microsoft Edge não encontrado")
    print("💡 Por favor, instale o Microsoft Edge antes de continuar")
    return False

def setup_selenium():
    """Configura Selenium para Power BI"""
    print("🔧 CONFIGURANDO SELENIUM PARA POWER BI")
    print("=" * 50)
    
    if not check_edge_installation():
        return False
    
    packages = ["selenium", "beautifulsoup4", "requests"]
    
    print("\n📦 Instalando pacotes Python...")
    all_installed = True
    
    for package in packages:
        if not install_package(package):
            all_installed = False
    
    if not all_installed:
        print("❌ Alguns pacotes falharam na instalação")
        return False
    
    print("\n🚗 Configurando WebDriver...")
    if not download_edge_driver():
        print("❌ Falha ao configurar WebDriver")
        return False
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("✅ Todos os componentes foram instalados")
    print("🚀 Agora você pode executar: python powerbi_scraper.py")
    
    return True

# ==================== LIMPEZA PINECONE ====================

def delete_all_vectors():
    """Deleta todos os vetores do índice Pinecone"""
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        
        print("🗑️ Deletando todos os vetores do índice...")
        index.delete(delete_all=True)
        print("✅ Todos os vetores foram deletados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao deletar vetores: {e}")

# ==================== FUNÇÕES PRINCIPAIS ====================

def main_selenium_setup():
    """Função principal para configuração do Selenium"""
    success = setup_selenium()
    if not success:
        print("\n❌ Configuração falhou. Verifique os erros acima.")
        sys.exit(1)

def main_pinecone_cleanup():
    """Função principal para limpeza do Pinecone"""
    delete_all_vectors()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "selenium":
            main_selenium_setup()
        elif sys.argv[1] == "cleanup":
            main_pinecone_cleanup()
        else:
            print("Uso: python system_utils.py [selenium|cleanup]")
    else:
        print("Uso: python system_utils.py [selenium|cleanup]")