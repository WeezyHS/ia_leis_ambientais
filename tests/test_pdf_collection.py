"""
Script de teste para coleta de PDFs das leis ambientais
"""

import sys
import os
import json
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_lei_service import PDFLeiCollector

def test_pdf_collection():
    """Testa a coleta de PDFs das leis ambientais"""
    print("=== INICIANDO COLETA DE PDFs DAS LEIS AMBIENTAIS ===")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    collector = PDFLeiCollector()
    
    # Testa com apenas 5 páginas primeiro
    print("Coletando leis das primeiras 5 páginas...")
    leis_coletadas = collector.collect_all_pdf_laws(max_pages=5)
    
    print(f"\n=== RESULTADOS ===")
    print(f"Total de leis ambientais encontradas: {len(leis_coletadas)}")
    
    # Estatísticas
    leis_com_pdf = sum(1 for lei in leis_coletadas if lei['fonte'] == 'PDF')
    leis_sem_pdf = sum(1 for lei in leis_coletadas if lei['fonte'] == 'HTML')
    
    print(f"Leis com PDF processado: {leis_com_pdf}")
    print(f"Leis apenas com HTML: {leis_sem_pdf}")
    
    # Salva resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"tests/leis_pdf_teste_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(leis_coletadas, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados salvos em: {filename}")
    
    # Mostra exemplos
    print("\n=== EXEMPLOS DE LEIS COLETADAS ===")
    for i, lei in enumerate(leis_coletadas[:3]):
        print(f"\n{i+1}. {lei['titulo'][:80]}...")
        print(f"   Fonte: {lei['fonte']}")
        print(f"   Tamanho do conteúdo: {len(lei['conteudo'])} caracteres")
        print(f"   PDFs encontrados: {len(lei['pdf_links'])}")
    
    print(f"\nFim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return leis_coletadas

def test_full_collection():
    """Executa coleta completa de todas as páginas"""
    print("=== COLETA COMPLETA DE TODAS AS PÁGINAS ===")
    print("ATENÇÃO: Este processo pode demorar várias horas!")
    
    resposta = input("Deseja continuar? (s/N): ")
    if resposta.lower() != 's':
        print("Coleta cancelada.")
        return
    
    collector = PDFLeiCollector()
    leis_coletadas = collector.collect_all_pdf_laws(max_pages=250)
    
    # Salva resultado completo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"tests/leis_pdf_completas_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(leis_coletadas, f, ensure_ascii=False, indent=2)
    
    print(f"Coleta completa finalizada!")
    print(f"Total de leis: {len(leis_coletadas)}")
    print(f"Arquivo salvo: {filename}")
    
    return leis_coletadas

if __name__ == "__main__":
    # Executa teste com 5 páginas
    leis = test_pdf_collection()
    
    # Pergunta se quer fazer coleta completa
    if leis:
        print("\n" + "="*50)
        test_full_collection()