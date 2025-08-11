#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisar estrutura das leis no Pinecone
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
import json

# Carregar variáveis de ambiente
load_dotenv()

def analisar_estrutura_leis():
    """Analisa a estrutura das leis no Pinecone"""
    try:
        # Conectar ao Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("leis-ambientais")
        
        print("🔍 ANALISANDO ESTRUTURA DAS LEIS NO PINECONE")
        print("=" * 60)
        
        # Obter estatísticas do índice
        stats = index.describe_index_stats()
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"Total de vetores: {stats.total_vector_count}")
        print(f"Namespaces: {list(stats.namespaces.keys())}")
        
        for namespace, info in stats.namespaces.items():
            print(f"  {namespace or 'default'}: {info.vector_count} vetores")
        
        # Buscar amostras de diferentes tipos
        print(f"\n🔍 ANALISANDO AMOSTRAS DE DOCUMENTOS:")
        print("-" * 40)
        
        # Busca geral para ver estrutura
        query_result = index.query(
            vector=[0.1] * 1536,
            top_k=10,
            include_metadata=True
        )
        
        print(f"\n📋 ESTRUTURA DOS METADADOS (Amostra de {len(query_result.matches)} documentos):")
        
        estruturas_encontradas = {}
        tipos_documento = {}
        campos_metadata = set()
        
        for i, match in enumerate(query_result.matches):
            print(f"\n--- DOCUMENTO {i+1} ---")
            print(f"ID: {match.id}")
            print(f"Score: {match.score:.4f}")
            
            metadata = match.metadata
            print(f"Metadados disponíveis: {list(metadata.keys())}")
            
            # Coletar todos os campos de metadata
            campos_metadata.update(metadata.keys())
            
            # Analisar estrutura específica
            titulo = metadata.get('titulo', metadata.get('title', 'N/A'))
            descricao = metadata.get('descricao', metadata.get('description', 'N/A'))
            fonte = metadata.get('fonte', metadata.get('source', 'N/A'))
            tipo = metadata.get('tipo', metadata.get('type', 'N/A'))
            numero_lei = metadata.get('numero_lei', 'N/A')
            
            print(f"Título: {titulo[:100]}...")
            print(f"Descrição: {descricao[:100]}...")
            print(f"Fonte: {fonte}")
            print(f"Tipo: {tipo}")
            print(f"Número Lei: {numero_lei}")
            
            # Categorizar por tipo
            if tipo not in tipos_documento:
                tipos_documento[tipo] = 0
            tipos_documento[tipo] += 1
            
            # Identificar estrutura
            estrutura_key = f"{fonte}_{tipo}"
            if estrutura_key not in estruturas_encontradas:
                estruturas_encontradas[estrutura_key] = {
                    'campos': list(metadata.keys()),
                    'exemplo': metadata,
                    'count': 0
                }
            estruturas_encontradas[estrutura_key]['count'] += 1
        
        # Resumo das estruturas
        print(f"\n📊 RESUMO DAS ESTRUTURAS ENCONTRADAS:")
        print("=" * 60)
        
        print(f"\n🏷️ CAMPOS DE METADATA ÚNICOS ENCONTRADOS:")
        for campo in sorted(campos_metadata):
            print(f"  • {campo}")
        
        print(f"\n📂 TIPOS DE DOCUMENTO:")
        for tipo, count in tipos_documento.items():
            print(f"  • {tipo}: {count} documentos")
        
        print(f"\n🏗️ ESTRUTURAS POR FONTE/TIPO:")
        for estrutura, info in estruturas_encontradas.items():
            print(f"\n  📋 {estrutura} ({info['count']} documentos):")
            print(f"     Campos: {', '.join(info['campos'])}")
        
        # Buscar especificamente por leis federais
        print(f"\n🔍 BUSCANDO ESPECIFICAMENTE POR LEIS FEDERAIS:")
        print("-" * 50)
        
        # Tentar diferentes filtros para leis federais
        filtros_federais = [
            {"fonte": "Federal"},
            {"source": "Federal"},
            {"jurisdicao": "Federal"},
            {"tipo": "Lei Federal"},
            {"type": "Lei Federal"}
        ]
        
        leis_federais_encontradas = []
        
        for filtro in filtros_federais:
            try:
                print(f"\n🔎 Testando filtro: {filtro}")
                query_result = index.query(
                    vector=[0.1] * 1536,
                    top_k=5,
                    include_metadata=True,
                    filter=filtro
                )
                
                if query_result.matches:
                    print(f"  ✅ Encontrados {len(query_result.matches)} documentos")
                    for match in query_result.matches:
                        leis_federais_encontradas.append(match.metadata)
                        titulo = match.metadata.get('titulo', match.metadata.get('title', 'N/A'))
                        print(f"    • {titulo[:80]}...")
                else:
                    print(f"  ❌ Nenhum documento encontrado")
                    
            except Exception as e:
                print(f"  ⚠️ Erro com filtro {filtro}: {e}")
        
        # Buscar por termos relacionados a leis federais
        print(f"\n🔍 BUSCANDO POR TERMOS RELACIONADOS A LEIS FEDERAIS:")
        print("-" * 55)
        
        termos_federais = [
            "lei federal",
            "código florestal",
            "política nacional meio ambiente",
            "lei 6938",
            "lei 12651",
            "SNUC"
        ]
        
        for termo in termos_federais:
            try:
                print(f"\n🔎 Buscando por: '{termo}'")
                query_result = index.query(
                    vector=[0.1] * 1536,
                    top_k=3,
                    include_metadata=True
                )
                
                # Filtrar resultados que contenham o termo
                resultados_relevantes = []
                for match in query_result.matches:
                    metadata = match.metadata
                    texto_busca = f"{metadata.get('titulo', '')} {metadata.get('descricao', '')} {metadata.get('conteudo', '')}".lower()
                    if termo.lower() in texto_busca:
                        resultados_relevantes.append(match)
                
                if resultados_relevantes:
                    print(f"  ✅ Encontrados {len(resultados_relevantes)} documentos relevantes")
                    for match in resultados_relevantes:
                        titulo = match.metadata.get('titulo', match.metadata.get('title', 'N/A'))
                        print(f"    • {titulo[:80]}...")
                else:
                    print(f"  ❌ Nenhum documento relevante encontrado")
                    
            except Exception as e:
                print(f"  ⚠️ Erro buscando '{termo}': {e}")
        
        # Conclusão
        print(f"\n🎯 CONCLUSÃO SOBRE LEIS FEDERAIS:")
        print("=" * 40)
        
        if leis_federais_encontradas:
            print(f"✅ Foram encontradas {len(leis_federais_encontradas)} leis federais no Pinecone")
            print(f"📋 Estrutura típica das leis federais:")
            
            # Analisar estrutura das leis federais
            if leis_federais_encontradas:
                exemplo_lei_federal = leis_federais_encontradas[0]
                print(f"   Campos disponíveis: {list(exemplo_lei_federal.keys())}")
                
                # Verificar se já tem descrição
                tem_descricao = any(campo in exemplo_lei_federal for campo in ['descricao', 'description', 'descricao_resumida'])
                print(f"   Tem descrição: {'✅ SIM' if tem_descricao else '❌ NÃO'}")
                
                if tem_descricao:
                    for campo in ['descricao', 'description', 'descricao_resumida']:
                        if campo in exemplo_lei_federal:
                            descricao_atual = exemplo_lei_federal[campo]
                            print(f"   Campo '{campo}': {descricao_atual[:100]}...")
        else:
            print(f"❌ NÃO foram encontradas leis federais específicas no Pinecone")
            print(f"💡 Isso significa que:")
            print(f"   • As leis federais podem estar misturadas com outras leis")
            print(f"   • Não há campo específico para identificar leis federais")
            print(f"   • A integração com API do LexML seria ESSENCIAL")
        
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"   • Integrar API do LexML para obter descrições oficiais")
        print(f"   • Adicionar campo 'jurisdicao' para identificar leis federais")
        print(f"   • Enriquecer metadados com informações da API")
        
    except Exception as e:
        print(f"❌ Erro ao analisar estrutura: {e}")

if __name__ == "__main__":
    analisar_estrutura_leis()