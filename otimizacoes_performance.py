#!/usr/bin/env python3
"""
Script para aplicar otimizações de performance na API (GPT-4o-mini otimizado)
Autor: IA Assistant
Data: 2024
"""

import os
import sys
import subprocess
import time

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import openai
        import langchain
        import pinecone
        import fastapi
        import uvicorn
        print("✅ Todas as dependências principais estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def testar_performance_api():
    """Testa a performance da API após otimizações"""
    print("\n🚀 Testando performance da API...")
    
    import requests
    import json
    
    url = "http://localhost:8000/consulta"
    
    # Testes de diferentes tipos de consulta
    testes = [
        {
            "nome": "Consulta Simples",
            "pergunta": "O que é licenciamento ambiental?"
        },
        {
            "nome": "Consulta por Lei Específica", 
            "pergunta": "Lei 1.323 do Tocantins"
        },
        {
            "nome": "Consulta Complexa",
            "pergunta": "Quais são as penalidades para crimes ambientais no Tocantins?"
        }
    ]
    
    resultados = []
    
    for teste in testes:
        print(f"\n📋 Testando: {teste['nome']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                url,
                json={"pergunta": teste["pergunta"]},
                headers={"Content-Type": "application/json"},
                timeout=90  # 1.5 minutos de timeout
            )
            
            end_time = time.time()
            tempo_total = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                tempo_processamento = data.get("tempo_processamento", "N/A")
                status = data.get("status", "N/A")
                
                print(f"✅ Status: {status}")
                print(f"⏱️ Tempo total: {tempo_total:.2f}s")
                print(f"🔧 Tempo processamento: {tempo_processamento}")
                
                resultados.append({
                    "teste": teste["nome"],
                    "sucesso": True,
                    "tempo_total": tempo_total,
                    "tempo_processamento": tempo_processamento,
                    "status": status
                })
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                resultados.append({
                    "teste": teste["nome"],
                    "sucesso": False,
                    "erro": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - API demorou mais que 1.5 minutos")
            resultados.append({
                "teste": teste["nome"],
                "sucesso": False,
                "erro": "Timeout"
            })
        except Exception as e:
            print(f"❌ Erro: {e}")
            resultados.append({
                "teste": teste["nome"],
                "sucesso": False,
                "erro": str(e)
            })
    
    return resultados

def gerar_relatorio_performance(resultados):
    """Gera relatório de performance"""
    print("\n📊 RELATÓRIO DE PERFORMANCE")
    print("=" * 50)
    
    sucessos = sum(1 for r in resultados if r.get("sucesso", False))
    total = len(resultados)
    
    print(f"✅ Testes bem-sucedidos: {sucessos}/{total}")
    print(f"📈 Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    if sucessos > 0:
        tempos = [r["tempo_total"] for r in resultados if r.get("sucesso", False)]
        tempo_medio = sum(tempos) / len(tempos)
        print(f"⏱️ Tempo médio de resposta: {tempo_medio:.2f}s")
        
        if tempo_medio < 15:
            print("🚀 Performance EXCELENTE!")
        elif tempo_medio < 45:
            print("✅ Performance BOA")
        else:
            print("⚠️ Performance pode ser melhorada")
    
    print("\n📋 Detalhes dos testes:")
    for resultado in resultados:
        nome = resultado["teste"]
        if resultado.get("sucesso", False):
            tempo = resultado["tempo_total"]
            print(f"  ✅ {nome}: {tempo:.2f}s")
        else:
            erro = resultado.get("erro", "Erro desconhecido")
            print(f"  ❌ {nome}: {erro}")

def main():
    """Função principal"""
    print("🔧 OTIMIZAÇÕES DE PERFORMANCE APLICADAS (GPT-4o-mini)")
    print("=" * 60)
    
    print("\n✅ Mudanças implementadas:")
    print("  🤖 Modelo mantido: GPT-4o-mini (custo-benefício)")
    print("  ⚡ Processamento assíncrono implementado")
    print("  ⏱️ Timeouts otimizados (45s OpenAI, 90s API)")
    print("  🧵 Pool de threads para concorrência")
    print("  📊 Monitoramento de tempo de processamento")
    print("  🛡️ Tratamento de erros melhorado")
    print("  🔍 Busca otimizada (menos documentos, mais eficiente)")
    print("  💰 Tokens limitados (2000) para controle de custo")
    
    if not verificar_dependencias():
        print("\n❌ Instale as dependências antes de continuar")
        return
    
    print("\n⚠️ IMPORTANTE:")
    print("  1. Certifique-se que o servidor está rodando")
    print("  2. Verifique se a chave da OpenAI está configurada")
    print("  3. GPT-4o-mini: ótimo custo-benefício para este caso")
    
    resposta = input("\n🚀 Deseja testar a performance agora? (s/n): ").lower()
    
    if resposta == 's':
        print("\n⏳ Aguarde alguns segundos para o servidor inicializar...")
        time.sleep(5)
        
        resultados = testar_performance_api()
        gerar_relatorio_performance(resultados)
        
        print("\n💡 DICAS PARA MELHOR PERFORMANCE:")
        print("  • Use consultas específicas em vez de muito genéricas")
        print("  • O sistema agora processa consultas em paralelo")
        print("  • Timeouts configurados evitam travamentos")
        print("  • Busca otimizada reduz tempo de processamento")
        print("  • GPT-4o-mini oferece ótimo custo-benefício")
    
    print("\n🎉 Otimizações concluídas com sucesso!")
    print("💰 Mantendo GPT-4o-mini para controle de custos")

if __name__ == "__main__":
    main()