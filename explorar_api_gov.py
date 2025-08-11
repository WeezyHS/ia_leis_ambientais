#!/usr/bin/env python3
"""
Script para explorar a API do Portal de Dados Abertos do Governo Federal
e verificar que dados de legislação ambiental estão disponíveis.
"""

import requests
import json
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

def explorar_api_dados_abertos():
    """Explora a API do Portal de Dados Abertos"""
    
    print("🔍 Explorando API do Portal de Dados Abertos...")
    
    # URL base da API
    base_url = "https://dados.gov.br/api/publico"
    
    try:
        # 1. Buscar datasets relacionados à legislação ambiental
        print("\n📋 Buscando datasets de legislação ambiental...")
        
        search_params = {
            'q': 'legislação ambiental',
            'rows': 20
        }
        
        response = requests.get(f"{base_url}/conjuntos-dados", params=search_params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrados {len(data.get('result', []))} datasets")
            
            for dataset in data.get('result', [])[:5]:  # Mostrar apenas os 5 primeiros
                print(f"\n📄 Dataset: {dataset.get('title', 'N/A')}")
                print(f"   Descrição: {dataset.get('notes', 'N/A')[:100]}...")
                print(f"   Organização: {dataset.get('organization', {}).get('title', 'N/A')}")
                print(f"   Tags: {[tag.get('name') for tag in dataset.get('tags', [])]}")
                
                # Verificar recursos disponíveis
                resources = dataset.get('resources', [])
                print(f"   Recursos: {len(resources)} arquivo(s)")
                for resource in resources[:2]:  # Mostrar apenas os 2 primeiros recursos
                    print(f"     - {resource.get('name', 'N/A')} ({resource.get('format', 'N/A')})")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
    
    # 2. Buscar especificamente por CONAMA
    print("\n🏛️ Buscando dados do CONAMA...")
    try:
        search_params = {
            'q': 'CONAMA',
            'rows': 10
        }
        
        response = requests.get(f"{base_url}/conjuntos-dados", params=search_params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrados {len(data.get('result', []))} datasets do CONAMA")
            
            for dataset in data.get('result', [])[:3]:
                print(f"\n📄 CONAMA Dataset: {dataset.get('title', 'N/A')}")
                print(f"   Descrição: {dataset.get('notes', 'N/A')[:150]}...")
        else:
            print(f"❌ Erro na busca CONAMA: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro ao buscar CONAMA: {e}")
    
    # 3. Buscar por IBAMA
    print("\n🌿 Buscando dados do IBAMA...")
    try:
        search_params = {
            'q': 'IBAMA',
            'rows': 10
        }
        
        response = requests.get(f"{base_url}/conjuntos-dados", params=search_params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrados {len(data.get('result', []))} datasets do IBAMA")
            
            for dataset in data.get('result', [])[:3]:
                print(f"\n📄 IBAMA Dataset: {dataset.get('title', 'N/A')}")
                print(f"   Descrição: {dataset.get('notes', 'N/A')[:150]}...")
        else:
            print(f"❌ Erro na busca IBAMA: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro ao buscar IBAMA: {e}")

def explorar_api_ibama_direto():
    """Explora a API do IBAMA diretamente"""
    
    print("\n🌿 Explorando API do IBAMA diretamente...")
    
    # URL da API do IBAMA
    ibama_url = "https://dadosabertos.ibama.gov.br/api/v1"
    
    try:
        # Tentar acessar endpoints conhecidos
        endpoints = [
            "/datasets",
            "/legislacao",
            "/normas",
            "/resolucoes"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{ibama_url}{endpoint}")
                print(f"📡 Endpoint {endpoint}: Status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Dados disponíveis: {len(data) if isinstance(data, list) else 'Objeto'}")
                
            except Exception as e:
                print(f"   ❌ Erro no endpoint {endpoint}: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral na API IBAMA: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando exploração das APIs do Governo Federal...")
    
    explorar_api_dados_abertos()
    explorar_api_ibama_direto()
    
    print("\n✅ Exploração concluída!")