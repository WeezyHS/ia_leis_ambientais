#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar dados federais no Pinecone
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Carregar variáveis de ambiente
load_dotenv()

def verificar_dados_federais():
    """Verifica se existem dados federais no Pinecone"""
    try:
        # Configurar Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(os.getenv('PINECONE_INDEX_NAME', 'leis-ambientais'))

        # Verificar estatísticas
        stats = index.describe_index_stats()
        print('Namespaces disponíveis:')
        for ns, info in stats.namespaces.items():
            print(f'  {ns}: {info.vector_count} vetores')

        # Tentar buscar dados federais no namespace padrão
        print('\n🔍 Buscando dados federais...')
        
        # Buscar por diferentes filtros
        filtros = [
            {'source': 'CONAMA'},
            {'source': 'IBAMA'},
            {'source': 'ICMBio'},
            {'source': 'Federal'},
            {'jurisdicao': 'Federal'},
            {'esfera': 'Federal'}
        ]
        
        total_encontrados = 0
        
        for filtro in filtros:
            try:
                query_result = index.query(
                    vector=[0.1] * 1536,  # Vector dummy
                    top_k=10,
                    include_metadata=True,
                    filter=filtro
                )
                
                if query_result.matches:
                    print(f'\n📋 Filtro {filtro}: {len(query_result.matches)} documentos')
                    total_encontrados += len(query_result.matches)
                    
                    for i, match in enumerate(query_result.matches[:3]):  # Mostrar apenas os 3 primeiros
                        print(f'  {i+1}. ID: {match.id}')
                        print(f'     Source: {match.metadata.get("source", "N/A")}')
                        print(f'     Title: {match.metadata.get("title", "N/A")}')
                        print(f'     Text: {match.metadata.get("text", "N/A")[:100]}...')
                        print('     ---')
                        
            except Exception as e:
                print(f'Erro com filtro {filtro}: {e}')
        
        # Buscar sem filtro para ver todos os dados
        print('\n🔍 Buscando todos os dados (amostra)...')
        try:
            query_result = index.query(
                vector=[0.1] * 1536,
                top_k=10,
                include_metadata=True
            )
            
            print(f'Total de documentos encontrados: {len(query_result.matches)}')
            
            # Analisar fontes disponíveis
            fontes = set()
            for match in query_result.matches:
                fonte = match.metadata.get('source', 'N/A')
                fontes.add(fonte)
            
            print(f'Fontes encontradas: {list(fontes)}')
            
        except Exception as e:
            print(f'Erro na busca geral: {e}')
        
        print(f'\n📊 Total de documentos federais encontrados: {total_encontrados}')
        
        return total_encontrados > 0
        
    except Exception as e:
        print(f'❌ Erro ao conectar com Pinecone: {e}')
        return False

if __name__ == "__main__":
    verificar_dados_federais()