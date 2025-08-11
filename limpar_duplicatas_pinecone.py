#!/usr/bin/env python3
"""
Script para limpeza de duplicatas no Pinecone
Remove documentos duplicados mantendo apenas uma cópia de cada
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dotenv import load_dotenv
from pinecone import Pinecone
from difflib import SequenceMatcher

# Carregar variáveis de ambiente
load_dotenv()

def calcular_hash_texto(texto: str) -> str:
    """Calcula hash MD5 do texto normalizado"""
    if not texto:
        return ""
    texto_normalizado = texto.lower().strip()
    return hashlib.md5(texto_normalizado.encode('utf-8')).hexdigest()

def similaridade_texto(texto1: str, texto2: str) -> float:
    """Calcula similaridade entre dois textos (0-1)"""
    if not texto1 or not texto2:
        return 0.0
    return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

def extrair_identificador_metadata(metadata: dict) -> str:
    """Extrai identificador único dos metadados"""
    identificadores = []
    
    # Campos que podem servir como identificadores
    campos_id = ['id', 'titulo', 'title', 'nome', 'name', 'url', 'link']
    
    for campo in campos_id:
        if campo in metadata and metadata[campo]:
            valor = str(metadata[campo]).strip()
            if valor:
                identificadores.append(f"{campo}:{calcular_hash_texto(valor)}")
    
    return "|".join(identificadores) if identificadores else ""

def buscar_documentos_por_namespace(pinecone_index, namespace: str, limite_por_consulta: int = 100) -> List[Dict]:
    """Busca documentos em um namespace específico"""
    documentos = []
    
    print(f"🔍 Buscando documentos no namespace: '{namespace}'")
    
    try:
        # Tentar consulta com vetor dummy
        vetor_dummy = [0.1] * 1536  # Dimensão padrão OpenAI
        
        resultados = pinecone_index.query(
            vector=vetor_dummy,
            top_k=limite_por_consulta,
            namespace=namespace,
            include_metadata=True
        )
        
        for match in resultados.matches:
            doc = {
                'id': match.id,
                'namespace': namespace,
                'metadata': match.metadata or {},
                'score': match.score
            }
            documentos.append(doc)
            
        print(f"✅ Encontrados {len(documentos)} documentos no namespace '{namespace}'")
        
    except Exception as e:
        print(f"❌ Erro ao buscar documentos no namespace '{namespace}': {e}")
    
    return documentos

def identificar_duplicatas_para_remocao(documentos: List[Dict]) -> Tuple[List[str], Dict]:
    """
    Identifica quais documentos devem ser removidos (duplicatas)
    Retorna: (lista_ids_para_remover, relatorio_duplicatas)
    """
    print(f"🔍 Analisando {len(documentos)} documentos para identificar duplicatas...")
    
    # Agrupar por hash de texto
    grupos_por_texto = {}
    grupos_por_identificador = {}
    
    for doc in documentos:
        # Extrair texto dos metadados
        metadata = doc['metadata']
        texto = metadata.get('text', '') or metadata.get('content', '') or metadata.get('titulo', '')
        
        # Agrupar por hash de texto
        hash_texto = calcular_hash_texto(texto)
        if hash_texto and hash_texto != calcular_hash_texto(""):
            if hash_texto not in grupos_por_texto:
                grupos_por_texto[hash_texto] = []
            grupos_por_texto[hash_texto].append(doc)
        
        # Agrupar por identificador de metadados
        identificador = extrair_identificador_metadata(metadata)
        if identificador:
            if identificador not in grupos_por_identificador:
                grupos_por_identificador[identificador] = []
            grupos_por_identificador[identificador].append(doc)
    
    # Identificar duplicatas por texto
    ids_para_remover = set()
    duplicatas_texto = {}
    
    for hash_texto, docs_grupo in grupos_por_texto.items():
        if len(docs_grupo) > 1:
            # Manter o primeiro documento, remover os outros
            docs_ordenados = sorted(docs_grupo, key=lambda x: x['id'])
            manter = docs_ordenados[0]
            remover = docs_ordenados[1:]
            
            duplicatas_texto[hash_texto] = {
                'mantido': manter['id'],
                'removidos': [doc['id'] for doc in remover],
                'titulo': manter['metadata'].get('titulo', 'Sem título'),
                'total_duplicatas': len(docs_grupo)
            }
            
            # Adicionar IDs para remoção
            for doc in remover:
                ids_para_remover.add(doc['id'])
    
    # Identificar duplicatas por identificador (que não foram pegas por texto)
    duplicatas_identificador = {}
    
    for identificador, docs_grupo in grupos_por_identificador.items():
        if len(docs_grupo) > 1:
            # Verificar se já não foram identificadas como duplicatas de texto
            docs_nao_removidos = [doc for doc in docs_grupo if doc['id'] not in ids_para_remover]
            
            if len(docs_nao_removidos) > 1:
                # Manter o primeiro documento, remover os outros
                docs_ordenados = sorted(docs_nao_removidos, key=lambda x: x['id'])
                manter = docs_ordenados[0]
                remover = docs_ordenados[1:]
                
                duplicatas_identificador[identificador] = {
                    'mantido': manter['id'],
                    'removidos': [doc['id'] for doc in remover],
                    'titulo': manter['metadata'].get('titulo', 'Sem título'),
                    'total_duplicatas': len(docs_nao_removidos)
                }
                
                # Adicionar IDs para remoção
                for doc in remover:
                    ids_para_remover.add(doc['id'])
    
    relatorio = {
        'total_documentos_analisados': len(documentos),
        'total_ids_para_remover': len(ids_para_remover),
        'duplicatas_por_texto': duplicatas_texto,
        'duplicatas_por_identificador': duplicatas_identificador,
        'ids_para_remover': list(ids_para_remover)
    }
    
    print(f"📊 Duplicatas identificadas:")
    print(f"   - Por texto: {len(duplicatas_texto)} grupos")
    print(f"   - Por identificador: {len(duplicatas_identificador)} grupos")
    print(f"   - Total de IDs para remover: {len(ids_para_remover)}")
    
    return list(ids_para_remover), relatorio

def remover_documentos_pinecone(pinecone_index, ids_para_remover: List[str], namespace: str, lote_size: int = 100) -> Dict:
    """Remove documentos do Pinecone em lotes"""
    print(f"🗑️ Iniciando remoção de {len(ids_para_remover)} documentos do namespace '{namespace}'...")
    
    removidos_com_sucesso = []
    erros = []
    
    # Processar em lotes
    for i in range(0, len(ids_para_remover), lote_size):
        lote = ids_para_remover[i:i + lote_size]
        
        try:
            print(f"   Removendo lote {i//lote_size + 1}: {len(lote)} documentos...")
            
            # Remover do Pinecone
            pinecone_index.delete(ids=lote, namespace=namespace)
            
            removidos_com_sucesso.extend(lote)
            print(f"   ✅ Lote removido com sucesso")
            
        except Exception as e:
            print(f"   ❌ Erro ao remover lote: {e}")
            erros.extend([(id_doc, str(e)) for id_doc in lote])
    
    resultado = {
        'total_solicitados': len(ids_para_remover),
        'removidos_com_sucesso': len(removidos_com_sucesso),
        'erros': len(erros),
        'ids_removidos': removidos_com_sucesso,
        'detalhes_erros': erros
    }
    
    print(f"📊 Resultado da remoção:")
    print(f"   - Solicitados: {resultado['total_solicitados']}")
    print(f"   - Removidos: {resultado['removidos_com_sucesso']}")
    print(f"   - Erros: {resultado['erros']}")
    
    return resultado

def limpar_duplicatas_completo():
    """Função principal para limpeza completa de duplicatas"""
    print("🧹 INICIANDO LIMPEZA DE DUPLICATAS NO PINECONE")
    print("=" * 60)
    
    # Inicializar Pinecone
    try:
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'leis-ambientais')
        
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY não encontrada nas variáveis de ambiente")
        
        print(f"🔗 Conectando ao Pinecone (índice: {pinecone_index_name})...")
        pc = Pinecone(api_key=pinecone_api_key)
        pinecone_index = pc.Index(pinecone_index_name)
        
        print("✅ Conexão estabelecida com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Pinecone: {e}")
        return
    
    # Obter estatísticas antes da limpeza
    try:
        stats_antes = pinecone_index.describe_index_stats()
        print(f"📊 Estatísticas ANTES da limpeza:")
        print(f"   - Total de vetores: {stats_antes.total_vector_count}")
        print(f"   - Namespaces: {list(stats_antes.namespaces.keys()) if stats_antes.namespaces else ['padrão']}")
        
        for namespace, info in (stats_antes.namespaces or {}).items():
            print(f"   - Namespace '{namespace}': {info.vector_count} vetores")
        
    except Exception as e:
        print(f"⚠️ Erro ao obter estatísticas: {e}")
        stats_antes = None
    
    # Processar cada namespace
    namespaces_para_processar = ['abnt-normas', '']  # Baseado na análise anterior
    
    relatorio_geral = {
        'timestamp': datetime.now().isoformat(),
        'stats_antes': stats_antes.to_dict() if stats_antes else None,
        'namespaces_processados': {},
        'total_removidos': 0,
        'total_erros': 0
    }
    
    for namespace in namespaces_para_processar:
        print(f"\n🔄 Processando namespace: '{namespace}'")
        print("-" * 40)
        
        # Buscar documentos
        documentos = buscar_documentos_por_namespace(pinecone_index, namespace)
        
        if not documentos:
            print(f"⚠️ Nenhum documento encontrado no namespace '{namespace}'")
            continue
        
        # Identificar duplicatas
        ids_para_remover, relatorio_duplicatas = identificar_duplicatas_para_remocao(documentos)
        
        if not ids_para_remover:
            print(f"✅ Nenhuma duplicata encontrada no namespace '{namespace}'")
            relatorio_geral['namespaces_processados'][namespace] = {
                'documentos_analisados': len(documentos),
                'duplicatas_encontradas': 0,
                'documentos_removidos': 0,
                'relatorio_duplicatas': relatorio_duplicatas
            }
            continue
        
        # Confirmar remoção
        print(f"\n⚠️ ATENÇÃO: Serão removidos {len(ids_para_remover)} documentos duplicados do namespace '{namespace}'")
        print("Exemplos de duplicatas que serão removidas:")
        
        for i, (grupo, info) in enumerate(relatorio_duplicatas['duplicatas_por_texto'].items()):
            if i >= 3:  # Mostrar apenas 3 exemplos
                break
            print(f"   - '{info['titulo']}' ({info['total_duplicatas']} cópias)")
        
        confirmacao = input("\nDeseja prosseguir com a remoção? (s/N): ").strip().lower()
        
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print(f"❌ Remoção cancelada para namespace '{namespace}'")
            continue
        
        # Executar remoção
        resultado_remocao = remover_documentos_pinecone(pinecone_index, ids_para_remover, namespace)
        
        # Atualizar relatório geral
        relatorio_geral['namespaces_processados'][namespace] = {
            'documentos_analisados': len(documentos),
            'duplicatas_encontradas': len(ids_para_remover),
            'documentos_removidos': resultado_remocao['removidos_com_sucesso'],
            'erros_remocao': resultado_remocao['erros'],
            'relatorio_duplicatas': relatorio_duplicatas,
            'resultado_remocao': resultado_remocao
        }
        
        relatorio_geral['total_removidos'] += resultado_remocao['removidos_com_sucesso']
        relatorio_geral['total_erros'] += resultado_remocao['erros']
    
    # Obter estatísticas após a limpeza
    try:
        stats_depois = pinecone_index.describe_index_stats()
        relatorio_geral['stats_depois'] = stats_depois.to_dict()
        
        print(f"\n📊 Estatísticas DEPOIS da limpeza:")
        print(f"   - Total de vetores: {stats_depois.total_vector_count}")
        
        for namespace, info in (stats_depois.namespaces or {}).items():
            print(f"   - Namespace '{namespace}': {info.vector_count} vetores")
        
    except Exception as e:
        print(f"⚠️ Erro ao obter estatísticas finais: {e}")
        relatorio_geral['stats_depois'] = None
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_relatorio = f"relatorio_limpeza_pinecone_{timestamp}.json"
    
    try:
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio_geral, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {arquivo_relatorio}")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar relatório: {e}")
    
    # Resumo final
    print(f"\n🎯 RESUMO FINAL DA LIMPEZA")
    print("=" * 40)
    print(f"✅ Total de documentos removidos: {relatorio_geral['total_removidos']}")
    print(f"❌ Total de erros: {relatorio_geral['total_erros']}")
    
    if stats_antes and relatorio_geral['stats_depois']:
        reducao = stats_antes.total_vector_count - relatorio_geral['stats_depois']['total_vector_count']
        print(f"📉 Redução total de vetores: {reducao}")
    
    print(f"📄 Relatório detalhado: {arquivo_relatorio}")
    print("\n🎉 Limpeza concluída!")

if __name__ == "__main__":
    limpar_duplicatas_completo()