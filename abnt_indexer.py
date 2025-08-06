#!/usr/bin/env python3
"""
Indexador de Normas ABNT para Pinecone
Integra os dados coletados da ABNT ao sistema de IA
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
import hashlib
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# Carrega variáveis de ambiente
load_dotenv()

class ABNTIndexer:
    def __init__(self):
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = PineconeVectorStore(index_name=self.index_name, embedding=self.embeddings)
        self.namespace = "abnt-normas"  # Namespace específico para ABNT
        
    def load_abnt_data(self, file_path: str = "abnt_consolidated_results.json") -> List[Dict]:
        """Carrega dados consolidados da ABNT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrai normas únicas dos dados aninhados
            normas = []
            
            for categoria, categoria_data in data.items():
                if isinstance(categoria_data, dict) and 'results' in categoria_data:
                    for item in categoria_data['results']:
                        if isinstance(item, dict) and 'code' in item:
                            # Extrai código, título e preço do campo 'code'
                            code_text = item['code']
                            lines = code_text.strip().split('\n')
                            
                            if len(lines) >= 3:
                                codigo = lines[0].strip()
                                titulo = lines[2].strip()
                                
                                # Procura por preço (BRL)
                                preco = ""
                                for line in lines:
                                    if 'BRL' in line:
                                        preco = line.strip()
                                        break
                                
                                norma = {
                                    'codigo': codigo,
                                    'titulo': titulo,
                                    'preco': preco,
                                    'categoria': categoria
                                }
                                
                                # Evita duplicatas
                                if not any(n['codigo'] == codigo for n in normas):
                                    normas.append(norma)
            
            print(f"✅ Extraídas {len(normas)} normas únicas da ABNT")
            return normas
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return []
    
    def create_document_content(self, item: Dict) -> str:
        """Cria conteúdo textual otimizado para busca semântica"""
        content_parts = []
        
        # Código da norma (mais importante)
        if item.get('codigo'):
            content_parts.append(f"Código: {item['codigo']}")
        
        # Título completo
        if item.get('titulo'):
            content_parts.append(f"Título: {item['titulo']}")
        
        # Preço
        if item.get('preco'):
            content_parts.append(f"Preço: {item['preco']}")
        
        # Ano (extraído do código)
        if item.get('codigo'):
            # Extrai ano do código (ex: ABNT NBR ISO 14040:2025 -> 2025)
            import re
            year_match = re.search(r':(\d{4})', item['codigo'])
            if year_match:
                content_parts.append(f"Ano: {year_match.group(1)}")
        
        # Categoria baseada no título
        titulo_lower = item.get('titulo', '').lower()
        categorias = []
        
        if any(word in titulo_lower for word in ['environmental', 'ambiental', 'meio ambiente']):
            categorias.append("Gestão Ambiental")
        if any(word in titulo_lower for word in ['esg', 'governance', 'social']):
            categorias.append("ESG")
        if any(word in titulo_lower for word in ['water', 'água', 'hídrico']):
            categorias.append("Recursos Hídricos")
        if any(word in titulo_lower for word in ['waste', 'resíduo', 'lixo']):
            categorias.append("Gestão de Resíduos")
        if any(word in titulo_lower for word in ['soil', 'solo', 'contaminação']):
            categorias.append("Solo e Contaminação")
        if any(word in titulo_lower for word in ['life cycle', 'ciclo de vida']):
            categorias.append("Avaliação do Ciclo de Vida")
        if any(word in titulo_lower for word in ['green debt', 'dívida verde']):
            categorias.append("Instrumentos Financeiros Verdes")
        
        if categorias:
            content_parts.append(f"Categorias: {', '.join(categorias)}")
        
        # Palavras-chave para busca
        keywords = []
        if 'ISO 14001' in item.get('codigo', ''):
            keywords.append("sistema de gestão ambiental")
        if 'ISO 14040' in item.get('codigo', ''):
            keywords.append("avaliação do ciclo de vida")
        if 'ISO 14030' in item.get('codigo', ''):
            keywords.append("instrumentos de dívida verde")
        if 'PR 2030' in item.get('codigo', ''):
            keywords.append("ESG governança ambiental social")
        
        if keywords:
            content_parts.append(f"Palavras-chave: {', '.join(keywords)}")
        
        return "\n".join(content_parts)
    
    def create_metadata(self, item: Dict) -> Dict:
        """Cria metadados estruturados"""
        metadata = {
            'source': 'ABNT',
            'tipo': 'norma_tecnica',
            'codigo': item.get('codigo', ''),
            'titulo': item.get('titulo', ''),
            'preco': item.get('preco', ''),
            'data_coleta': datetime.now().isoformat(),
            'namespace': self.namespace
        }
        
        # Extrai ano do código
        if item.get('codigo'):
            import re
            year_match = re.search(r':(\d{4})', item['codigo'])
            if year_match:
                metadata['ano'] = year_match.group(1)
        
        # Determina tipo de norma
        codigo = item.get('codigo', '')
        if 'NBR ISO' in codigo:
            metadata['tipo_norma'] = 'NBR_ISO'
        elif 'PR' in codigo:
            metadata['tipo_norma'] = 'Projeto_Revisao'
        elif 'NBR' in codigo:
            metadata['tipo_norma'] = 'NBR'
        
        return metadata
    
    def index_abnt_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Indexa dados da ABNT no Pinecone"""
        try:
            documents = []
            
            for item in data:
                # Cria conteúdo e metadados
                content = self.create_document_content(item)
                metadata = self.create_metadata(item)
                
                # Cria ID único baseado no código
                doc_id = hashlib.md5(f"abnt_{item.get('codigo', '')}".encode()).hexdigest()
                metadata['id'] = doc_id
                
                # Cria documento
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                documents.append(doc)
            
            print(f"📝 Preparados {len(documents)} documentos para indexação...")
            
            # Indexa no Pinecone com namespace específico
            self.vectorstore.add_documents(
                documents=documents,
                namespace=self.namespace
            )
            
            print(f"✅ {len(documents)} normas ABNT indexadas com sucesso!")
            
            return {
                'success': True,
                'total_indexed': len(documents),
                'namespace': self.namespace,
                'message': f'Indexadas {len(documents)} normas ABNT no namespace {self.namespace}'
            }
            
        except Exception as e:
            print(f"❌ Erro na indexação: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Falha na indexação das normas ABNT'
            }
    
    def test_search(self, query: str = "ABNT NBR ISO 14040:2025") -> List[Dict]:
        """Testa busca nas normas indexadas"""
        try:
            print(f"🔍 Testando busca por: '{query}'")
            
            # Busca sem namespace (LangChain pode não suportar namespace na busca)
            results = self.vectorstore.similarity_search(
                query=query,
                k=5
            )
            
            # Filtra resultados do namespace ABNT
            abnt_results = []
            for doc in results:
                if doc.metadata.get('namespace') == self.namespace:
                    abnt_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    })
            
            print(f"📊 Encontrados {len(abnt_results)} resultados da ABNT")
            for i, result in enumerate(abnt_results, 1):
                print(f"\n{i}. {result['metadata'].get('codigo', 'N/A')}")
                print(f"   Título: {result['metadata'].get('titulo', 'N/A')}")
                print(f"   Preço: {result['metadata'].get('preco', 'N/A')}")
            
            return abnt_results
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []

def main():
    """Função principal"""
    print("🚀 Iniciando indexação das normas ABNT...")
    
    indexer = ABNTIndexer()
    
    # Carrega dados
    data = indexer.load_abnt_data()
    if not data:
        print("❌ Nenhum dado encontrado para indexar")
        return
    
    # Indexa dados
    result = indexer.index_abnt_data(data)
    
    if result['success']:
        print(f"\n🎉 Indexação concluída com sucesso!")
        print(f"📊 Total indexado: {result['total_indexed']} normas")
        print(f"🏷️ Namespace: {result['namespace']}")
        
        # Testa busca
        print(f"\n🧪 Testando busca...")
        indexer.test_search("ABNT NBR ISO 14040:2025")
        indexer.test_search("ESG governança ambiental")
        indexer.test_search("gestão de resíduos")
        
    else:
        print(f"❌ Falha na indexação: {result['message']}")

if __name__ == "__main__":
    main()