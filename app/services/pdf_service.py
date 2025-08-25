from typing import List, Dict, Any
import PyPDF2
import io
from fastapi import UploadFile

class PDFService:
    """Serviço para processamento de arquivos PDF"""
    
    @staticmethod
    def extract_text_from_bytes(content: bytes) -> str:
        """Extrai texto de um arquivo PDF a partir de bytes
        
        Args:
            content: Conteúdo do arquivo PDF em bytes
            
        Returns:
            str: Texto extraído do PDF
        """
        try:
            # Cria um objeto BytesIO para o PyPDF2
            pdf_file = io.BytesIO(content)
            
            # Cria o leitor PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extrai texto de todas as páginas
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
    
    @staticmethod
    async def extract_text_from_pdf(file: UploadFile) -> str:
        """Extrai texto de um arquivo PDF
        
        Args:
            file: Arquivo PDF enviado pelo usuário
            
        Returns:
            str: Texto extraído do PDF
        """
        try:
            # Lê o conteúdo do arquivo
            content = await file.read()
            
            # Usa o método síncrono para extrair texto
            return PDFService.extract_text_from_bytes(content)
            
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
        finally:
            # Reseta o ponteiro do arquivo para o início
            await file.seek(0)
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Divide o texto em chunks menores para processamento
        
        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho máximo de cada chunk
            overlap: Sobreposição entre chunks
            
        Returns:
            List[str]: Lista de chunks de texto
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Define o fim do chunk
            end = start + chunk_size
            
            # Se não é o último chunk, tenta quebrar em uma palavra
            if end < len(text):
                # Procura por espaço ou quebra de linha próxima
                while end > start and text[end] not in [' ', '\n', '.', '!', '?']:
                    end -= 1
                
                # Se não encontrou um bom ponto de quebra, usa o tamanho original
                if end == start:
                    end = start + chunk_size
            
            # Adiciona o chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move o início para o próximo chunk com sobreposição
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    @staticmethod
    def process_pdf(content: bytes) -> List[str]:
        """Processa um arquivo PDF a partir de bytes
        
        Args:
            content: Conteúdo do arquivo PDF em bytes
            
        Returns:
            List[str]: Lista de chunks de texto extraídos
        """
        try:
            # Extrai o texto
            text = PDFService.extract_text_from_bytes(content)
            
            # Divide em chunks
            chunks = PDFService.chunk_text(text)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    @staticmethod
    async def process_pdf_upload(file: UploadFile) -> Dict[str, Any]:
        """Processa um arquivo PDF completo
        
        Args:
            file: Arquivo PDF enviado pelo usuário
            
        Returns:
            Dict: Informações do arquivo processado
        """
        try:
            # Extrai o texto
            text = await PDFService.extract_text_from_pdf(file)
            
            # Divide em chunks
            chunks = PDFService.chunk_text(text)
            
            return {
                "filename": file.filename,
                "size": file.size,
                "text": text,
                "chunks": chunks,
                "num_chunks": len(chunks),
                "text_length": len(text)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")

# Instância global do serviço
pdf_service = PDFService()