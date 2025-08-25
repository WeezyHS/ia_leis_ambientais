from typing import List, Dict, Optional
from datetime import datetime
import uuid

class DocumentChatService:
    """
    Serviço para gerenciar contexto de documentos carregados e conversas baseadas em documentos.
    """
    
    # Armazenamento em memória dos documentos processados
    _documents: Dict[str, Dict] = {}
    _document_chats: Dict[str, List[Dict]] = {}
    
    @classmethod
    def store_document(cls, document_id: str, filename: str, chunks: List[str]) -> str:
        """
        Armazena um documento processado em chunks.
        
        Args:
            document_id: ID único do documento
            filename: Nome do arquivo original
            chunks: Lista de chunks de texto extraídos do documento
            
        Returns:
            str: ID do documento armazenado
        """
        cls._documents[document_id] = {
            'id': document_id,
            'filename': filename,
            'chunks': chunks,
            'created_at': datetime.now().isoformat(),
            'total_chunks': len(chunks)
        }
        
        # Inicializa lista de conversas para este documento
        cls._document_chats[document_id] = []
        
        return document_id
    
    @classmethod
    def get_document(cls, document_id: str) -> Optional[Dict]:
        """
        Recupera informações de um documento armazenado.
        
        Args:
            document_id: ID do documento
            
        Returns:
            Dict: Informações do documento ou None se não encontrado
        """
        return cls._documents.get(document_id)
    
    @classmethod
    def search_relevant_chunks(cls, document_id: str, query: str, max_chunks: int = 3) -> List[str]:
        """
        Busca chunks relevantes do documento baseado na query.
        Por simplicidade, retorna os primeiros chunks. Em uma implementação
        mais avançada, usaria embeddings e similaridade semântica.
        
        Args:
            document_id: ID do documento
            query: Pergunta/query do usuário
            max_chunks: Número máximo de chunks a retornar
            
        Returns:
            List[str]: Lista de chunks relevantes
        """
        document = cls.get_document(document_id)
        if not document:
            return []
        
        chunks = document['chunks']
        
        # Implementação simples: busca por palavras-chave
        query_words = query.lower().split()
        scored_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            if score > 0:
                scored_chunks.append((score, i, chunk))
        
        # Ordena por relevância e retorna os melhores
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Se não encontrou chunks relevantes, retorna os primeiros
        if not scored_chunks:
            return chunks[:max_chunks]
        
        return [chunk for _, _, chunk in scored_chunks[:max_chunks]]
    
    @classmethod
    def add_chat_message(cls, document_id: str, role: str, content: str) -> None:
        """
        Adiciona uma mensagem ao histórico de chat do documento.
        
        Args:
            document_id: ID do documento
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
        """
        if document_id not in cls._document_chats:
            cls._document_chats[document_id] = []
        
        cls._document_chats[document_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    @classmethod
    def get_chat_history(cls, document_id: str) -> List[Dict]:
        """
        Recupera o histórico de chat de um documento.
        
        Args:
            document_id: ID do documento
            
        Returns:
            List[Dict]: Lista de mensagens do chat
        """
        return cls._document_chats.get(document_id, [])
    
    @classmethod
    def build_context_prompt(cls, document_id: str, user_question: str) -> str:
        """
        Constrói um prompt com contexto do documento para enviar à IA.
        
        Args:
            document_id: ID do documento
            user_question: Pergunta do usuário
            
        Returns:
            str: Prompt formatado com contexto
        """
        document = cls.get_document(document_id)
        if not document:
            return user_question
        
        relevant_chunks = cls.search_relevant_chunks(document_id, user_question)
        
        context_prompt = f"""Baseado no seguinte documento '{document['filename']}', responda à pergunta do usuário.

Conteúdo relevante do documento:
{chr(10).join(f"Trecho {i+1}: {chunk}" for i, chunk in enumerate(relevant_chunks))}

Pergunta do usuário: {user_question}

Responda baseando-se exclusivamente no conteúdo do documento fornecido. Se a informação não estiver disponível no documento, informe que não foi possível encontrar a resposta no documento carregado."""
        
        return context_prompt
    
    @classmethod
    def list_documents(cls) -> List[Dict]:
        """
        Lista todos os documentos armazenados.
        
        Returns:
            List[Dict]: Lista de informações dos documentos
        """
        return [
            {
                'id': doc_id,
                'filename': doc['filename'],
                'created_at': doc['created_at'],
                'total_chunks': doc['total_chunks']
            }
            for doc_id, doc in cls._documents.items()
        ]
    
    @classmethod
    def delete_document(cls, document_id: str) -> bool:
        """
        Remove um documento e seu histórico de chat.
        
        Args:
            document_id: ID do documento
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
        """
        if document_id in cls._documents:
            del cls._documents[document_id]
            if document_id in cls._document_chats:
                del cls._document_chats[document_id]
            return True
        return False
    
    @classmethod
    def generate_document_id(cls) -> str:
        """
        Gera um ID único para um novo documento.
        
        Returns:
            str: ID único
        """
        return str(uuid.uuid4())