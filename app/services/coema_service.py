"""
Serviço para integração dos dados do COEMA (Conselho Estadual de Meio Ambiente)
Processa e indexa documentos oficiais do COEMA no Pinecone
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
import re
from app.services.pinecone_service import vectorstore
from app.services.text_normalizer import normalizar_texto

class COEMAService:
    def __init__(self):
        self.namespace = "coema"
        
    def load_coema_documents(self, file_path: str = None) -> List[Dict[str, Any]]:
        """Carrega documentos do COEMA do arquivo JSON"""
        if not file_path:
            # Busca pelos arquivos de dados do COEMA
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            possible_files = [
                os.path.join(base_dir, "coema_official_documents.json"),
                os.path.join(base_dir, "coema_documents.json"),
                os.path.join(base_dir, "coema_data.json")
            ]
            
            for file_path in possible_files:
                if os.path.exists(file_path):
                    break
            else:
                raise FileNotFoundError("Nenhum arquivo de dados do COEMA encontrado")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            print(f"✅ Carregados {len(documents)} documentos do COEMA de {file_path}")
            return documents
            
        except Exception as e:
            print(f"❌ Erro ao carregar documentos do COEMA: {e}")
            return []
    
    def process_coema_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um documento do COEMA para indexação"""
        
        # Extrai informações básicas
        title = document.get('title', '').strip()
        content = document.get('content', '').strip()
        doc_type = document.get('type', 'documento')
        year = document.get('year', '')
        url = document.get('url', '')
        
        # Normaliza o texto
        normalized_text = normalizar_texto(content)
        normalized_title = normalizar_texto(title)
        
        # Extrai metadados adicionais
        metadata = {
            'source': 'COEMA',
            'type': doc_type,
            'year': year,
            'url': url,
            'title': title,
            'extracted_at': document.get('extracted_at', ''),
            'content_length': len(content)
        }
        
        # Extrai números de leis/resoluções/portarias se houver
        law_numbers = self.extract_law_numbers(content + " " + title)
        if law_numbers:
            metadata['law_numbers'] = law_numbers
        
        # Cria chunks do documento se for muito grande
        chunks = self.create_document_chunks(normalized_content, title, metadata)
        
        return {
            'title': title,
            'content': normalized_content,
            'metadata': metadata,
            'chunks': chunks
        }
    
    def extract_law_numbers(self, text: str) -> List[str]:
        """Extrai números de leis, resoluções, portarias, etc."""
        patterns = [
            r'(?:Lei|LEI)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)',
            r'(?:Resolução|RESOLUÇÃO)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)',
            r'(?:Portaria|PORTARIA)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)',
            r'(?:Decreto|DECRETO)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)',
            r'(?:Deliberação|DELIBERAÇÃO)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)',
            r'(?:Normativa|NORMATIVA)\s*n?[°º]?\s*(\d+(?:[./]\d+)*)'
        ]
        
        law_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            law_numbers.extend(matches)
        
        return list(set(law_numbers))  # Remove duplicatas
    
    def create_document_chunks(self, content: str, title: str, metadata: Dict[str, Any], 
                             chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Cria chunks de um documento para melhor indexação"""
        
        if len(content) <= chunk_size:
            return [{
                'text': content,
                'metadata': {**metadata, 'chunk_index': 0, 'total_chunks': 1}
            }]
        
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Adiciona contexto do título no início de cada chunk
            if title and not chunk_text.startswith(title[:50]):
                chunk_text = f"{title[:50]}... {chunk_text}"
            
            chunk_metadata = {
                **metadata,
                'chunk_index': len(chunks),
                'chunk_start': i,
                'chunk_end': min(i + chunk_size, len(words))
            }
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        # Atualiza total de chunks em todos os metadados
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)
        
        return chunks
    
    def process_coema_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa uma lista de documentos do COEMA"""
        processed_docs = []
        
        for doc in documents:
            try:
                # Adapta o formato dos dados coletados para o formato esperado
                processed_doc = {
                    'title': doc.get('title', ''),
                    'content': doc.get('text', ''),  # 'text' é o campo dos dados coletados
                    'metadata': {
                        'source': 'COEMA',
                        'type': doc.get('type', 'documento'),
                        'url': doc.get('url', ''),
                        'title': doc.get('title', ''),
                        'conselho': doc.get('conselho', 'COEMA'),
                        'collected_at': doc.get('collected_at', ''),
                        'content_length': len(doc.get('text', '')),
                        'conteudo': doc.get('text', '')  # Campo esperado pelo indexador
                    }
                }
                
                # Extrai números de leis/resoluções se houver
                text_content = doc.get('text', '') + " " + doc.get('title', '')
                law_numbers = self.extract_law_numbers(text_content)
                if law_numbers:
                    processed_doc['metadata']['law_numbers'] = law_numbers
                
                processed_docs.append(processed_doc)
                
            except Exception as e:
                print(f"Erro ao processar documento: {e}")
                continue
        
        return processed_docs
    
    def index_coema_documents(self, documents_path: str = None) -> dict:
        """Indexa documentos do COEMA no Pinecone"""
        try:
            if not documents_path:
                documents_path = "coema_official_documents.json"
            
            documents = self.load_coema_documents(documents_path)
            if not documents:
                return {"success": False, "message": "Nenhum documento encontrado"}
            
            processed_docs = self.process_coema_documents(documents)
            
            # Converte para formato do LangChain
            from langchain_core.documents import Document
            langchain_docs = []
            for doc in processed_docs:
                langchain_docs.append(Document(
                    page_content=doc["metadata"]["conteudo"],
                    metadata={**doc["metadata"], "namespace": self.namespace}
                ))
            
            # Indexa no Pinecone
            vectorstore.add_documents(langchain_docs)
            
            return {
                "success": True,
                "message": f"{len(processed_docs)} documentos do COEMA indexados com sucesso",
                "documents_count": len(processed_docs)
            }
        except Exception as e:
            return {"success": False, "message": f"Erro ao indexar documentos: {str(e)}"}
    
    def search_coema_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos do COEMA usando similaridade semântica"""
        try:
            # Normaliza a query
            normalized_query = normalizar_texto(query)
            
            # Busca documentos com filtro de namespace
            docs = vectorstore.similarity_search(
                query=normalized_query,
                k=top_k,
                filter={"namespace": self.namespace}
            )
            
            # Converte para formato esperado
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.8  # Score padrão já que similarity_search não retorna score
                })
            
            return results
            
        except Exception as e:
            print(f"Erro na busca do COEMA: {e}")
            return []
    
    def get_coema_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice COEMA"""
        try:
            # Como não temos acesso direto às estatísticas do Pinecone via LangChain,
            # retornamos informações básicas
            return {
                'namespace': self.namespace,
                'status': 'active',
                'message': 'Estatísticas detalhadas não disponíveis via LangChain'
            }
            
        except Exception as e:
            return {
                'namespace': self.namespace,
                'error': str(e),
                'status': 'error'
            }
    
    def delete_coema_namespace(self) -> Dict[str, Any]:
        """Remove todos os documentos do namespace COEMA"""
        try:
            # Como não temos acesso direto à remoção de namespace via LangChain,
            # retornamos uma mensagem informativa
            return {
                'success': False,
                'message': 'Remoção de namespace não disponível via LangChain. Use o console do Pinecone.',
                'namespace': self.namespace
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}',
                'namespace': self.namespace
            }

def main():
    """Função principal para indexar documentos do COEMA"""
    coema_service = COEMAService()
    result = coema_service.index_coema_documents()
    
    if result['success']:
        print(f"\n🎉 Indexação concluída com sucesso!")
        print(f"📊 {result['indexed_documents']} documentos indexados")
        print(f"📄 {result['total_chunks']} chunks criados")
    else:
        print(f"\n❌ Falha na indexação")
        if result.get('errors'):
            print("Erros encontrados:")
            for error in result['errors']:
                print(f"  • {error}")

if __name__ == "__main__":
    main()