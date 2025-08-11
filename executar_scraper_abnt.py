#!/usr/bin/env python3
"""
Script para executar o scraper da ABNT e coletar normas ambientais
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório app ao path
sys.path.append(str(Path(__file__).parent / "app"))

def main():
    """Executa o scraper da ABNT e salva os dados"""
    
    try:
        from services.multi_source_scraper import ABNTScraper
        
        print("🔧 Iniciando coleta de normas ABNT...")
        print("=" * 50)
        
        # Criar instância do scraper
        scraper = ABNTScraper()
        
        # Executar coleta
        print("📡 Coletando normas ambientais da ABNT...")
        documentos = scraper.extract_documents()
        
        if documentos:
            # Salvar dados coletados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_saida = f"abnt_normas_ambientais_{timestamp}.json"
            
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(documentos, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Coleta concluída!")
            print(f"📄 {len(documentos)} normas coletadas")
            print(f"💾 Dados salvos em: {arquivo_saida}")
            
            # Mostrar estatísticas
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   • Total de normas: {len(documentos)}")
            
            # Contar por status
            status_count = {}
            for doc in documentos:
                status = doc.get('status', 'N/A')
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in status_count.items():
                print(f"   • {status}: {count}")
            
            # Mostrar exemplos
            print(f"\n📋 EXEMPLOS DE NORMAS COLETADAS:")
            for i, doc in enumerate(documentos[:5]):
                print(f"   {i+1}. {doc.get('codigo', 'N/A')} - {doc.get('titulo', 'N/A')}")
            
            if len(documentos) > 5:
                print(f"   ... e mais {len(documentos) - 5} normas")
                
        else:
            print("❌ Nenhuma norma foi coletada")
            print("💡 Verifique a conexão com a internet e tente novamente")
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se todas as dependências estão instaladas")
        
    except Exception as e:
        print(f"❌ Erro durante a coleta: {e}")
        print("💡 Verifique os logs para mais detalhes")

if __name__ == "__main__":
    main()