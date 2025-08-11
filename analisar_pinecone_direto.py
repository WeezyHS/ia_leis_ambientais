#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Direta do Pinecone - Verificação de Duplicatas
Analisa dados do Pinecone sem usar embeddings OpenAI
"""

import os
import json
from datetime import datetime
from collections import defaultdict, Counter
import hashlib
from difflib import SequenceMatcher

# Importar componentes do Pinecone diretamente
from dotenv import load_dotenv
load_dotenv()

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

def fetch_all_vectors_from_namespace(pinecone_index, namespace, limit=1000):
    """Busca todos os vetores de um namespace usando fetch"""
    print(f"   🔍 Buscando vetores do namespace: {namespace}")
    
    # Primeiro, vamos tentar obter alguns IDs usando uma consulta dummy
    # Como não temos embeddings, vamos usar o método list_paginated se disponível
    
    vectors = []
    try:
        # Tentar usar query com vetor dummy para obter alguns IDs
        dummy_vector = [0.1] * 1536  # Dimensão padrão do text-embedding-3-small
        
        response = pinecone_index.query(
            vector=dummy_vector,
            top_k=min(limit, 10000),  # Máximo permitido pelo Pinecone
            namespace=namespace,
            include_metadata=True,
            include_values=False
        )
        
        for match in response.matches:
            vectors.append({
                'id': match.id,
                'metadata': match.metadata or {},
                'namespace': namespace
            })
            
    except Exception as e:
        print(f"   ⚠️ Erro na consulta do namespace {namespace}: {e}")
        
        # Método alternativo: tentar fetch com IDs conhecidos
        # Vamos tentar alguns padrões de ID comuns
        id_patterns = []
        
        # Padrões para diferentes fontes
        if namespace == "abnt-normas":
            # IDs típicos da ABNT
            for i in range(100):
                id_patterns.extend([
                    f"abnt_{i}",
                    f"abnt_norma_{i}",
                    f"nbr_{i}",
                    f"abnt-{i}"
                ])
        elif namespace == "":
            # Namespace padrão (leis)
            for i in range(100):
                id_patterns.extend([
                    f"lei_{i}",
                    f"lei_to_{i}",
                    f"tocantins_{i}",
                    f"coema_{i}"
                ])
        
        # Tentar fetch com os IDs
        for batch_start in range(0, len(id_patterns), 100):
            batch_ids = id_patterns[batch_start:batch_start + 100]
            try:
                fetch_response = pinecone_index.fetch(ids=batch_ids, namespace=namespace)
                for vector_id, vector_data in fetch_response.vectors.items():
                    vectors.append({
                        'id': vector_id,
                        'metadata': vector_data.metadata or {},
                        'namespace': namespace
                    })
            except Exception as fetch_error:
                continue
    
    print(f"   ✅ Encontrados {len(vectors)} vetores no namespace {namespace}")
    return vectors

def analisar_duplicatas_direto():
    """Análise direta de duplicatas no Pinecone"""
    print("🔍 INICIANDO ANÁLISE DIRETA DO PINECONE")
    print("=" * 60)
    
    try:
        # Inicializar conexão Pinecone
        index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
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
            
            # Buscar todos os vetores do namespace
            documentos_namespace = fetch_all_vectors_from_namespace(
                pinecone_index, 
                namespace_name, 
                limit=namespace_count
            )
            
            # Adicionar à lista geral
            for doc in documentos_namespace:
                todos_documentos.append(doc)
            
            por_namespace[namespace_name] = documentos_namespace
            total_processados += len(documentos_namespace)
        
        print(f"\n📈 TOTAL DE DOCUMENTOS PROCESSADOS: {total_processados}")
        
        if total_processados == 0:
            print("\n❌ NENHUM DOCUMENTO FOI EXTRAÍDO!")
            print("Isso pode indicar:")
            print("- Problemas de conectividade com o Pinecone")
            print("- Configuração incorreta de API keys")
            print("- Estrutura de IDs diferente do esperado")
            print("- Namespaces vazios ou inacessíveis")
            return None
        
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
            # Tentar diferentes campos de texto
            texto = (metadata.get('content', '') or 
                    metadata.get('texto', '') or 
                    metadata.get('text', '') or
                    metadata.get('conteudo', '') or
                    metadata.get('description', '') or
                    metadata.get('descricao', ''))
            
            if texto and len(texto) > 50:  # Só considerar textos com conteúdo significativo
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
                    titulo = (metadata.get('title', '') or 
                             metadata.get('titulo', '') or 
                             metadata.get('lei_numero', '') or
                             metadata.get('norma_numero', ''))
                    fonte = metadata.get('source', 'N/A')
                    print(f"     {i+1}. ID: {doc['id'][:30]}... | Fonte: {fonte} | Título: {titulo[:50]}...")
        
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
                    print(f"     {i+1}. ID: {doc['id'][:30]}... | Fonte: {fonte} | Namespace: {doc['namespace']}")
        
        # 5. Análise de IDs duplicados
        print(f"\n🔍 ANALISANDO IDs DUPLICADOS...")
        ids_count = Counter([doc['id'] for doc in todos_documentos])
        ids_duplicados = {id_val: count for id_val, count in ids_count.items() if count > 1}
        
        if ids_duplicados:
            duplicatas_encontradas = True
            print(f"\n🚨 IDs DUPLICADOS: {len(ids_duplicados)}")
            for id_val, count in ids_duplicados.items():
                print(f"   ID: {id_val} aparece {count} vezes")
                docs_com_id = [doc for doc in todos_documentos if doc['id'] == id_val]
                for doc in docs_com_id:
                    print(f"     - Namespace: {doc['namespace']} | Fonte: {doc['metadata'].get('source', 'N/A')}")
        
        # 6. Resumo final
        print(f"\n📊 RESUMO FINAL DA ANÁLISE")
        print("=" * 60)
        print(f"Total de documentos analisados: {len(todos_documentos)}")
        print(f"Namespaces: {len(por_namespace)}")
        print(f"Fontes diferentes: {len(por_fonte)}")
        print(f"Duplicatas por texto: {len(duplicatas_texto)}")
        print(f"Duplicatas por identificador: {len(duplicatas_ids)}")
        print(f"IDs duplicados: {len(ids_duplicados)}")
        
        if not duplicatas_encontradas:
            print(f"\n✅ NENHUMA DUPLICATA ENCONTRADA!")
            print("Todos os documentos parecem ser únicos.")
        else:
            print(f"\n⚠️ DUPLICATAS DETECTADAS!")
            print("Verifique os detalhes acima para mais informações.")
        
        # 7. Salvar relatório detalhado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = f"relatorio_pinecone_direto_{timestamp}.json"
        
        relatorio = {
            'timestamp': timestamp,
            'total_documentos': len(todos_documentos),
            'por_namespace': {k: len(v) for k, v in por_namespace.items()},
            'por_fonte': {k: len(v) for k, v in por_fonte.items()},
            'duplicatas_texto': len(duplicatas_texto),
            'duplicatas_identificadores': len(duplicatas_ids),
            'ids_duplicados': len(ids_duplicados),
            'duplicatas_encontradas': duplicatas_encontradas,
            'detalhes_duplicatas_texto': {
                h: [{'id': d['id'], 'fonte': d['metadata'].get('source', 'N/A')} for d in docs]
                for h, docs in duplicatas_texto.items()
            },
            'detalhes_duplicatas_ids': {
                k: [{'id': d['id'], 'fonte': d['metadata'].get('source', 'N/A')} for d in docs]
                for k, docs in duplicatas_ids.items()
            },
            'detalhes_ids_duplicados': {
                id_val: [{'namespace': d['namespace'], 'fonte': d['metadata'].get('source', 'N/A')} for d in todos_documentos if d['id'] == id_val]
                for id_val in ids_duplicados.keys()
            },
            'amostra_documentos': [
                {
                    'id': doc['id'],
                    'namespace': doc['namespace'],
                    'fonte': doc['metadata'].get('source', 'N/A'),
                    'titulo': (doc['metadata'].get('title', '') or 
                              doc['metadata'].get('titulo', '') or 
                              doc['metadata'].get('lei_numero', ''))[:100]
                }
                for doc in todos_documentos[:20]  # Primeiros 20 como amostra
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
    resultado = analisar_duplicatas_direto()
    
    if resultado:
        print(f"\n🎯 ANÁLISE CONCLUÍDA COM SUCESSO!")
        if resultado['duplicatas_encontradas']:
            print(f"⚠️ Foram encontradas duplicatas - verifique o relatório detalhado.")
        else:
            print(f"✅ Nenhuma duplicata encontrada - base de dados limpa!")
    else:
        print(f"\n❌ Falha na análise - verifique os logs de erro.")