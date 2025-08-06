"""
Indexador para múltiplas fontes de dados
Integra o sistema de coleta multi-fonte com o Pinecone
"""

import sys
import os
import json
import hashlib
from typing import List, Dict

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.multi_source_scraper import MultiSourceCollector
from app.services.embedding_service import gerar_embedding
from app.services.pinecone_service import indexar_no_pinecone
from app.services.lei_filter import filtrar_leis_revogadas
from langchain.text_splitter import RecursiveCharacterTextSplitter

class MultiSourceIndexer:
    """Indexador para múltiplas fontes de dados"""
    
    def __init__(self):
        self.collector = MultiSourceCollector()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def collect_and_index(self):
        """Coleta dados de todas as fontes e indexa no Pinecone"""
        print("=== INICIANDO COLETA DE MÚLTIPLAS FONTES ===")
        
        # 1. Coleta dados de todas as fontes
        documents = self.collector.collect_all_sources()
        
        if not documents:
            print("Nenhum documento foi coletado.")
            return
            
        print(f"\nTotal de documentos coletados: {len(documents)}")
        
        # 2. Filtra leis revogadas
        print("\nFiltrando leis revogadas...")
        documents = filtrar_leis_revogadas(documents)
        print(f"Documentos após filtro: {len(documents)}")
        
        # 3. Salva backup dos dados coletados
        self.collector.save_to_file(documents, "backup_multi_source.json")
        
        # 4. Processa e indexa cada documento
        self._process_and_index_documents(documents)
        
    def _process_and_index_documents(self, documents: List[Dict]):
        """Processa e indexa os documentos coletados"""
        print("\n=== PROCESSANDO E INDEXANDO DOCUMENTOS ===")
        
        items_to_index = []
        
        for doc in documents:
            try:
                # Divide o texto em chunks
                chunks = self.text_splitter.split_text(doc['text'])
                
                for i, chunk in enumerate(chunks):
                    # Cria ID único para o chunk
                    chunk_id = self._generate_chunk_id(doc, i)
                    
                    # Gera embedding
                    embedding = gerar_embedding(chunk)
                    
                    # Prepara metadados
                    metadata = {
                        'titulo': f"{doc['source']} - Chunk {i+1}",
                        'descricao': f"Documento de {doc['source']} ({doc['type']})",
                        'conteudo': chunk,
                        'source': doc['source'],
                        'url': doc['url'],
                        'type': doc['type'],
                        'collected_at': doc['collected_at'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                    
                    items_to_index.append({
                        'id': chunk_id,
                        'values': embedding,
                        'metadata': metadata
                    })
                    
                print(f"Processado: {doc['source']} - {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Erro ao processar documento de {doc['source']}: {e}")
                continue
                
        # Indexa todos os itens no Pinecone
        if items_to_index:
            print(f"\nIndexando {len(items_to_index)} chunks no Pinecone...")
            indexar_no_pinecone(items_to_index)
            print("Indexação concluída!")
        else:
            print("Nenhum item para indexar.")
            
    def _generate_chunk_id(self, doc: Dict, chunk_index: int) -> str:
        """Gera ID único para um chunk"""
        base_string = f"{doc['source']}_{doc['url']}_{chunk_index}"
        return hashlib.md5(base_string.encode('utf-8')).hexdigest()
        
    def add_custom_source(self, source_name: str, documents: List[Dict]):
        """Permite adicionar documentos de uma fonte customizada"""
        print(f"\n=== ADICIONANDO FONTE CUSTOMIZADA: {source_name} ===")
        
        # Formata documentos para o padrão esperado
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                'source': source_name,
                'url': doc.get('url', 'N/A'),
                'text': doc['text'],
                'type': doc.get('type', 'custom'),
                'collected_at': doc.get('collected_at', 'N/A')
            })
            
        self._process_and_index_documents(formatted_docs)
        
    def load_and_index_from_file(self, filename: str):
        """Carrega documentos de um arquivo JSON e indexa"""
        print(f"\n=== CARREGANDO E INDEXANDO DE: {filename} ===")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                documents = json.load(f)
                
            self._process_and_index_documents(documents)
            
        except Exception as e:
            print(f"Erro ao carregar arquivo {filename}: {e}")

def main():
    """Função principal"""
    indexer = MultiSourceIndexer()
    
    # Opção 1: Coleta e indexa de todas as fontes configuradas
    indexer.collect_and_index()
    
    # Opção 2: Exemplo de como adicionar uma fonte customizada
    # custom_docs = [
    #     {
    #         'text': 'Texto da lei customizada...',
    #         'url': 'https://exemplo.com/lei1',
    #         'type': 'html'
    #     }
    # ]
    # indexer.add_custom_source("Fonte Customizada", custom_docs)
    
    # Opção 3: Exemplo de como carregar de um arquivo
    # indexer.load_and_index_from_file("meus_documentos.json")

if __name__ == "__main__":
    main()