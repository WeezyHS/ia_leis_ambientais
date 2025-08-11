#!/usr/bin/env python3
"""
Script para verificar se a limpeza de duplicatas foi bem-sucedida
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from pinecone import Pinecone

# Carregar variáveis de ambiente
load_dotenv()

def calcular_hash_texto(texto: str) -> str:
    """Calcula hash MD5 do texto normalizado"""
    if not texto:
        return ""
    texto_normalizado = texto.lower().strip()
    return hashlib.md5(texto_normalizado.encode('utf-8')).hexdigest()

def buscar_documentos_por_namespace(pinecone_index, namespace: str, limite_por_consulta: int = 100) -> List[Dict]:
    """Busca documentos em um namespace específico"""
    documentos = []
    
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
            
    except Exception as e:
        print(f"❌ Erro ao buscar documentos no namespace '{namespace}': {e}")
    
    return documentos

def verificar_duplicatas_pos_limpeza():
    """Verifica se ainda existem duplicatas após a limpeza"""
    print("🔍 VERIFICANDO LIMPEZA DE DUPLICATAS NO PINECONE")
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
    
    # Obter estatísticas atuais
    try:
        stats = pinecone_index.describe_index_stats()
        print(f"📊 Estatísticas atuais:")
        print(f"   - Total de vetores: {stats.total_vector_count}")
        
        for namespace, info in (stats.namespaces or {}).items():
            print(f"   - Namespace '{namespace}': {info.vector_count} vetores")
        
    except Exception as e:
        print(f"⚠️ Erro ao obter estatísticas: {e}")
    
    # Verificar cada namespace
    namespaces = ['abnt-normas', '']
    relatorio_verificacao = {
        'timestamp': datetime.now().isoformat(),
        'stats_atuais': stats.to_dict() if 'stats' in locals() else None,
        'verificacao_por_namespace': {}
    }
    
    for namespace in namespaces:
        print(f"\n🔄 Verificando namespace: '{namespace}'")
        print("-" * 40)
        
        # Buscar documentos
        documentos = buscar_documentos_por_namespace(pinecone_index, namespace)
        
        if not documentos:
            print(f"⚠️ Nenhum documento encontrado no namespace '{namespace}'")
            continue
        
        print(f"📄 Encontrados {len(documentos)} documentos")
        
        # Verificar duplicatas por hash de texto
        grupos_por_hash = {}
        titulos_unicos = set()
        titulos_duplicados = []
        
        for doc in documentos:
            metadata = doc['metadata']
            texto = metadata.get('text', '') or metadata.get('content', '') or metadata.get('titulo', '')
            titulo = metadata.get('titulo', 'Sem título')
            
            # Verificar hash de texto
            hash_texto = calcular_hash_texto(texto)
            if hash_texto and hash_texto != calcular_hash_texto(""):
                if hash_texto not in grupos_por_hash:
                    grupos_por_hash[hash_texto] = []
                grupos_por_hash[hash_texto].append({
                    'id': doc['id'],
                    'titulo': titulo
                })
            
            # Verificar títulos duplicados
            if titulo and titulo != 'Sem título':
                if titulo in titulos_unicos:
                    titulos_duplicados.append(titulo)
                else:
                    titulos_unicos.add(titulo)
        
        # Identificar duplicatas restantes
        duplicatas_encontradas = {}
        for hash_texto, docs in grupos_por_hash.items():
            if len(docs) > 1:
                duplicatas_encontradas[hash_texto] = docs
        
        # Relatório do namespace
        relatorio_namespace = {
            'total_documentos': len(documentos),
            'duplicatas_por_hash': len(duplicatas_encontradas),
            'titulos_duplicados': len(set(titulos_duplicados)),
            'detalhes_duplicatas': duplicatas_encontradas,
            'lista_titulos_duplicados': list(set(titulos_duplicados))
        }
        
        relatorio_verificacao['verificacao_por_namespace'][namespace] = relatorio_namespace
        
        # Exibir resultados
        if duplicatas_encontradas:
            print(f"⚠️ AINDA EXISTEM DUPLICATAS:")
            print(f"   - {len(duplicatas_encontradas)} grupos de duplicatas por hash")
            for hash_texto, docs in duplicatas_encontradas.items():
                print(f"   - Hash {hash_texto[:8]}...: {len(docs)} documentos")
                for doc in docs:
                    print(f"     * {doc['id']}: {doc['titulo']}")
        else:
            print(f"✅ NENHUMA DUPLICATA ENCONTRADA por hash de texto")
        
        if titulos_duplicados:
            print(f"⚠️ Títulos duplicados encontrados: {len(set(titulos_duplicados))}")
            for titulo in set(titulos_duplicados):
                print(f"   - '{titulo}'")
        else:
            print(f"✅ NENHUM título duplicado encontrado")
    
    # Salvar relatório de verificação
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_verificacao = f"verificacao_limpeza_pinecone_{timestamp}.json"
    
    try:
        with open(arquivo_verificacao, 'w', encoding='utf-8') as f:
            json.dump(relatorio_verificacao, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório de verificação salvo em: {arquivo_verificacao}")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar relatório: {e}")
    
    # Resumo final
    total_duplicatas = sum(
        info['duplicatas_por_hash'] 
        for info in relatorio_verificacao['verificacao_por_namespace'].values()
    )
    
    print(f"\n🎯 RESUMO DA VERIFICAÇÃO")
    print("=" * 40)
    
    if total_duplicatas == 0:
        print("✅ LIMPEZA BEM-SUCEDIDA!")
        print("✅ Nenhuma duplicata encontrada em nenhum namespace")
        print("✅ Banco de dados está limpo e otimizado")
    else:
        print(f"⚠️ AINDA EXISTEM {total_duplicatas} GRUPOS DE DUPLICATAS")
        print("⚠️ Pode ser necessária limpeza adicional")
    
    print(f"📄 Relatório detalhado: {arquivo_verificacao}")

if __name__ == "__main__":
    verificar_duplicatas_pos_limpeza()