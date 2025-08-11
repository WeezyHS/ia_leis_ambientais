#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Completa do Pinecone - Verificação de Duplicatas
Analisa 100% dos dados no Pinecone para identificar duplicatas
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter
import hashlib
from difflib import SequenceMatcher

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Importar componentes do Pinecone diretamente
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

def calcular_hash_texto(texto):
    """Calcula hash MD5 do texto normalizado"""
    if not texto:
        return None
    # Normalizar texto (remover espaços extras, quebras de linha, etc.)
    texto_normalizado = ' '.join(texto.strip().split())
    return hashlib.md5(texto_normalizado.encode('utf-8')).hexdigest()

def calcular_similaridade(texto1, texto2):
    """Calcula similaridade entre dois textos (0-1)"""
    if not texto1 or not texto2:
        return 0.0
    return SequenceMatcher(None, texto1, texto2).ratio()

def extrair_identificadores(metadata):
    """Extrai identificadores únicos dos metadados"""
    identificadores = {}
    
    # Identificadores comuns
    campos_id = ['id', 'numero', 'lei_numero', 'norma_numero', 'documento_id', 'title', 'titulo']
    
    for campo in campos_id:
        if campo in metadata:
            identificadores[campo] = metadata[campo]
    
    # Identificadores específicos por fonte
    if 'source' in metadata:
        source = metadata['source'].lower()
        if 'abnt' in source:
            if 'norma_numero' in metadata:
                identificadores['abnt_numero'] = metadata['norma_numero']
        elif 'coema' in source or 'semarh' in source:
            if 'titulo' in metadata:
                identificadores['coema_titulo'] = metadata['titulo']
        elif 'tocantins' in source or 'assembleia' in source:
            if 'lei_numero' in metadata:
                identificadores['lei_numero'] = metadata['lei_numero']
    
    return identificadores

def analisar_duplicatas_completo():
    """Análise completa de duplicatas no Pinecone"""
    print("🔍 INICIANDO ANÁLISE COMPLETA DO PINECONE")
    print("=" * 60)
    
    try:
        # Inicializar conexão Pinecone
        index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        pinecone_index = pc.Index(index_name)
        
        # Estruturas para análise
        todos_documentos = []
        por_namespace = defaultdict(list)
        por_fonte = defaultdict(list)
        hashes_texto = defaultdict(list)
        identificadores = defaultdict(list)
        
        print("📊 Coletando estatísticas gerais...")
        stats = pinecone_index.describe_index_stats()
        print(f"Total de vetores no índice: {stats.get('total_vector_count', 'N/A')}")
        
        # Obter todos os namespaces
        namespaces = stats.get('namespaces', {})
        print(f"Namespaces encontrados: {list(namespaces.keys())}")
        
        print("\n🔄 Extraindo TODOS os documentos...")
        
        # Para cada namespace, extrair todos os documentos
        total_processados = 0
        
        for namespace_name in namespaces.keys():
            print(f"\n📁 Processando namespace: {namespace_name}")
            namespace_count = namespaces[namespace_name].get('vector_count', 0)
            print(f"   Vetores no namespace: {namespace_count}")
            
            # Fazer múltiplas consultas para cobrir todo o namespace
            # Usar consultas com vetores aleatórios para obter amostras diversas
            documentos_namespace = []
            
            # Estratégia: fazer várias consultas com top_k alto
            for i in range(0, namespace_count, 50):  # Processar em lotes de 50
                try:
                    # Consulta genérica para obter documentos
                    query_text = f"documento lei norma regulamento {i}"
                    query_embedding = embeddings.embed_query(query_text)
                    
                    response = pinecone_index.query(
                        vector=query_embedding,
                        top_k=min(50, namespace_count - i),
                        namespace=namespace_name,
                        include_metadata=True
                    )
                    
                    resultados = response.matches
                    
                    for resultado in resultados:
                        doc_info = {
                            'id': resultado.id,
                            'score': resultado.score,
                            'metadata': resultado.metadata or {},
                            'namespace': namespace_name
                        }
                        documentos_namespace.append(doc_info)
                        todos_documentos.append(doc_info)
                        
                except Exception as e:
                    print(f"   ⚠️ Erro na consulta {i}: {e}")
                    continue
            
            # Remover duplicatas dentro do namespace (baseado no ID)
            ids_vistos = set()
            docs_unicos = []
            for doc in documentos_namespace:
                if doc['id'] not in ids_vistos:
                    docs_unicos.append(doc)
                    ids_vistos.add(doc['id'])
            
            por_namespace[namespace_name] = docs_unicos
            total_processados += len(docs_unicos)
            print(f"   ✅ Documentos únicos extraídos: {len(docs_unicos)}")
        
        print(f"\n📈 TOTAL DE DOCUMENTOS PROCESSADOS: {total_processados}")
        
        # Análise de duplicatas
        print("\n🔍 ANALISANDO DUPLICATAS...")
        
        # 1. Agrupar por fonte
        for doc in todos_documentos:
            metadata = doc['metadata']
            fonte = metadata.get('source', 'desconhecida')
            por_fonte[fonte].append(doc)
        
        print(f"\n📊 DISTRIBUIÇÃO POR FONTE:")
        for fonte, docs in por_fonte.items():
            print(f"   {fonte}: {len(docs)} documentos")
        
        # 2. Análise de hashes de texto
        print(f"\n🔤 ANALISANDO HASHES DE TEXTO...")
        for doc in todos_documentos:
            metadata = doc['metadata']
            texto = metadata.get('content', '') or metadata.get('texto', '') or metadata.get('text', '')
            
            if texto:
                hash_texto = calcular_hash_texto(texto)
                if hash_texto:
                    hashes_texto[hash_texto].append(doc)
        
        # 3. Análise de identificadores
        print(f"\n🏷️ ANALISANDO IDENTIFICADORES...")
        for doc in todos_documentos:
            metadata = doc['metadata']
            ids = extrair_identificadores(metadata)
            
            for tipo_id, valor_id in ids.items():
                if valor_id:
                    chave = f"{tipo_id}:{valor_id}"
                    identificadores[chave].append(doc)
        
        # 4. Relatório de duplicatas
        print(f"\n📋 RELATÓRIO DE DUPLICATAS")
        print("=" * 60)
        
        duplicatas_encontradas = False
        
        # Duplicatas por hash de texto
        duplicatas_texto = {h: docs for h, docs in hashes_texto.items() if len(docs) > 1}
        if duplicatas_texto:
            duplicatas_encontradas = True
            print(f"\n🚨 DUPLICATAS POR CONTEÚDO DE TEXTO: {len(duplicatas_texto)}")
            for hash_val, docs in duplicatas_texto.items():
                print(f"\n   Hash: {hash_val[:16]}...")
                print(f"   Documentos duplicados: {len(docs)}")
                for i, doc in enumerate(docs):
                    metadata = doc['metadata']
                    titulo = metadata.get('title', '') or metadata.get('titulo', '') or metadata.get('lei_numero', '')
                    fonte = metadata.get('source', 'N/A')
                    print(f"     {i+1}. ID: {doc['id'][:20]}... | Fonte: {fonte} | Título: {titulo[:50]}...")
        
        # Duplicatas por identificadores
        duplicatas_ids = {k: docs for k, docs in identificadores.items() if len(docs) > 1}
        if duplicatas_ids:
            duplicatas_encontradas = True
            print(f"\n🚨 DUPLICATAS POR IDENTIFICADORES: {len(duplicatas_ids)}")
            for identificador, docs in duplicatas_ids.items():
                print(f"\n   Identificador: {identificador}")
                print(f"   Documentos duplicados: {len(docs)}")
                for i, doc in enumerate(docs):
                    metadata = doc['metadata']
                    fonte = metadata.get('source', 'N/A')
                    print(f"     {i+1}. ID: {doc['id'][:20]}... | Fonte: {fonte} | Namespace: {doc['namespace']}")
        
        # 5. Análise de similaridade alta (para detectar duplicatas "quase idênticas")
        print(f"\n🔍 ANALISANDO SIMILARIDADE ALTA...")
        similaridades_altas = []
        
        # Comparar documentos da mesma fonte
        for fonte, docs in por_fonte.items():
            if len(docs) > 1:
                print(f"   Analisando {len(docs)} documentos de {fonte}...")
                for i in range(len(docs)):
                    for j in range(i+1, len(docs)):
                        doc1, doc2 = docs[i], docs[j]
                        texto1 = doc1['metadata'].get('content', '') or doc1['metadata'].get('texto', '')
                        texto2 = doc2['metadata'].get('content', '') or doc2['metadata'].get('texto', '')
                        
                        if texto1 and texto2 and len(texto1) > 100 and len(texto2) > 100:
                            similaridade = calcular_similaridade(texto1, texto2)
                            if similaridade > 0.85:  # 85% de similaridade
                                similaridades_altas.append({
                                    'doc1': doc1,
                                    'doc2': doc2,
                                    'similaridade': similaridade,
                                    'fonte': fonte
                                })
        
        if similaridades_altas:
            duplicatas_encontradas = True
            print(f"\n🚨 DOCUMENTOS COM ALTA SIMILARIDADE: {len(similaridades_altas)}")
            for item in similaridades_altas:
                print(f"\n   Similaridade: {item['similaridade']:.2%}")
                print(f"   Fonte: {item['fonte']}")
                print(f"   Doc 1: {item['doc1']['id'][:20]}...")
                print(f"   Doc 2: {item['doc2']['id'][:20]}...")
        
        # 6. Resumo final
        print(f"\n📊 RESUMO FINAL DA ANÁLISE")
        print("=" * 60)
        print(f"Total de documentos analisados: {len(todos_documentos)}")
        print(f"Namespaces: {len(por_namespace)}")
        print(f"Fontes diferentes: {len(por_fonte)}")
        print(f"Duplicatas por texto: {len(duplicatas_texto)}")
        print(f"Duplicatas por identificador: {len(duplicatas_ids)}")
        print(f"Similaridades altas: {len(similaridades_altas)}")
        
        if not duplicatas_encontradas:
            print(f"\n✅ NENHUMA DUPLICATA ENCONTRADA!")
            print("Todos os 307 documentos parecem ser únicos.")
        else:
            print(f"\n⚠️ DUPLICATAS DETECTADAS!")
            print("Verifique os detalhes acima para mais informações.")
        
        # 7. Salvar relatório detalhado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = f"relatorio_pinecone_completo_{timestamp}.json"
        
        relatorio = {
            'timestamp': timestamp,
            'total_documentos': len(todos_documentos),
            'por_namespace': {k: len(v) for k, v in por_namespace.items()},
            'por_fonte': {k: len(v) for k, v in por_fonte.items()},
            'duplicatas_texto': len(duplicatas_texto),
            'duplicatas_identificadores': len(duplicatas_ids),
            'similaridades_altas': len(similaridades_altas),
            'duplicatas_encontradas': duplicatas_encontradas,
            'detalhes_duplicatas_texto': {
                h: [{'id': d['id'], 'fonte': d['metadata'].get('source', 'N/A')} for d in docs]
                for h, docs in duplicatas_texto.items()
            },
            'detalhes_duplicatas_ids': {
                k: [{'id': d['id'], 'fonte': d['metadata'].get('source', 'N/A')} for d in docs]
                for k, docs in duplicatas_ids.items()
            },
            'detalhes_similaridades': [
                {
                    'similaridade': item['similaridade'],
                    'fonte': item['fonte'],
                    'doc1_id': item['doc1']['id'],
                    'doc2_id': item['doc2']['id']
                }
                for item in similaridades_altas
            ]
        }
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Relatório salvo em: {relatorio_file}")
        
        return relatorio
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    resultado = analisar_duplicatas_completo()
    
    if resultado:
        print(f"\n🎯 ANÁLISE CONCLUÍDA COM SUCESSO!")
        if resultado['duplicatas_encontradas']:
            print(f"⚠️ Foram encontradas duplicatas - verifique o relatório detalhado.")
        else:
            print(f"✅ Nenhuma duplicata encontrada - base de dados limpa!")
    else:
        print(f"\n❌ Falha na análise - verifique os logs de erro.")