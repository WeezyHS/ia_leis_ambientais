"""
Indexador aprimorado que coleta PDFs completos das leis ambientais
e os indexa no Pinecone para consultas mais precisas
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from app.services.pdf_lei_service import PDFLeiCollector
from app.services.indexar import vectorstore, gerar_id_unico
from langchain_core.documents import Document

class EnhancedLeiIndexer:
    """Indexador aprimorado com suporte a PDFs"""
    
    def __init__(self):
        self.collector = PDFLeiCollector()
        self.vectorstore = vectorstore
    
    def collect_and_index_pdf_laws(self, max_pages: int = 250, save_backup: bool = True):
        """
        Coleta leis ambientais com PDFs e indexa no Pinecone
        
        Args:
            max_pages: Número máximo de páginas para processar
            save_backup: Se deve salvar backup em JSON
        """
        print("=== INICIANDO COLETA E INDEXAÇÃO DE LEIS COM PDFs ===")
        
        # 1. Coleta leis com PDFs
        print("Coletando leis ambientais com conteúdo completo dos PDFs...")
        leis_coletadas = self.collector.collect_all_pdf_laws(max_pages)
        
        if not leis_coletadas:
            print("Nenhuma lei ambiental foi coletada.")
            return 0
        
        print(f"Total de leis ambientais coletadas: {len(leis_coletadas)}")
        
        # 2. Salva backup se solicitado
        if save_backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"tests/leis_pdf_backup_{timestamp}.json"
            
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(leis_coletadas, f, ensure_ascii=False, indent=2)
            
            print(f"Backup salvo em: {backup_file}")
        
        # 3. Prepara documentos para indexação
        print("Preparando documentos para indexação...")
        documentos = []
        ids = []
        
        for lei in leis_coletadas:
            # Cria conteúdo completo
            conteudo_completo = f"""TÍTULO: {lei['titulo']}

DESCRIÇÃO: {lei['descricao']}

CONTEÚDO COMPLETO:
{lei['conteudo']}"""
            
            # Cria metadados enriquecidos
            metadata = {
                "titulo": lei['titulo'],
                "descricao": lei['descricao'],
                "fonte": lei['fonte'],
                "tipo": "lei_estadual_tocantins",
                "categoria": "ambiental",
                "pdf_links": lei.get('pdf_links', []),
                "tamanho_conteudo": len(lei['conteudo']),
                "data_indexacao": datetime.now().isoformat()
            }
            
            # Gera ID único
            doc_id = gerar_id_unico(conteudo_completo)
            
            # Cria documento
            doc = Document(
                page_content=conteudo_completo,
                metadata=metadata
            )
            
            documentos.append(doc)
            ids.append(doc_id)
        
        # 4. Indexa no Pinecone
        print("Indexando documentos no Pinecone...")
        try:
            self.vectorstore.add_documents(documentos, ids=ids)
            print(f"✅ {len(documentos)} leis indexadas com sucesso!")
            
            # Estatísticas
            leis_com_pdf = sum(1 for lei in leis_coletadas if lei['fonte'] == 'PDF')
            leis_sem_pdf = sum(1 for lei in leis_coletadas if lei['fonte'] == 'HTML')
            
            print(f"📊 Estatísticas:")
            print(f"   - Leis com PDF completo: {leis_com_pdf}")
            print(f"   - Leis apenas com HTML: {leis_sem_pdf}")
            print(f"   - Total indexado: {len(documentos)}")
            
            return len(documentos)
            
        except Exception as e:
            print(f"❌ Erro ao indexar documentos: {e}")
            return 0
    
    def update_existing_laws(self):
        """Atualiza leis existentes com conteúdo completo dos PDFs"""
        print("=== ATUALIZANDO LEIS EXISTENTES COM PDFs ===")
        
        # Carrega leis existentes do backup mais recente
        backup_files = [f for f in os.listdir("tests") if f.startswith("leis_pdf_backup_")]
        
        if not backup_files:
            print("Nenhum backup encontrado. Execute collect_and_index_pdf_laws primeiro.")
            return 0
        
        # Usa o backup mais recente
        latest_backup = sorted(backup_files)[-1]
        backup_path = f"tests/{latest_backup}"
        
        print(f"Carregando backup: {backup_path}")
        
        with open(backup_path, "r", encoding="utf-8") as f:
            leis_coletadas = json.load(f)
        
        return self.index_laws_from_data(leis_coletadas)
    
    def index_laws_from_data(self, leis_data: List[Dict]) -> int:
        """Indexa leis a partir de dados já coletados"""
        print(f"Indexando {len(leis_data)} leis...")
        
        documentos = []
        ids = []
        
        for lei in leis_data:
            conteudo_completo = f"""TÍTULO: {lei['titulo']}

DESCRIÇÃO: {lei['descricao']}

CONTEÚDO COMPLETO:
{lei['conteudo']}"""
            
            metadata = {
                "titulo": lei['titulo'],
                "descricao": lei['descricao'],
                "fonte": lei.get('fonte', 'HTML'),
                "tipo": "lei_estadual_tocantins",
                "categoria": "ambiental",
                "pdf_links": lei.get('pdf_links', []),
                "tamanho_conteudo": len(lei['conteudo']),
                "data_indexacao": datetime.now().isoformat()
            }
            
            doc_id = gerar_id_unico(conteudo_completo)
            doc = Document(page_content=conteudo_completo, metadata=metadata)
            
            documentos.append(doc)
            ids.append(doc_id)
        
        try:
            self.vectorstore.add_documents(documentos, ids=ids)
            print(f"✅ {len(documentos)} leis indexadas com sucesso!")
            return len(documentos)
        except Exception as e:
            print(f"❌ Erro ao indexar: {e}")
            return 0

def main():
    """Função principal para execução do indexador"""
    indexer = EnhancedLeiIndexer()
    
    print("Escolha uma opção:")
    print("1. Coleta completa e indexação (todas as páginas)")
    print("2. Coleta de teste (5 páginas)")
    print("3. Indexar a partir de backup existente")
    
    opcao = input("Digite sua opção (1-3): ")
    
    if opcao == "1":
        return indexer.collect_and_index_pdf_laws(max_pages=250)
    elif opcao == "2":
        return indexer.collect_and_index_pdf_laws(max_pages=5)
    elif opcao == "3":
        return indexer.update_existing_laws()
    else:
        print("Opção inválida.")
        return 0

if __name__ == "__main__":
    main()