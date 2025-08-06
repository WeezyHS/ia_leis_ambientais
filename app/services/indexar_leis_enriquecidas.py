"""
Script para indexar leis ambientais enriquecidas no Pinecone
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from app.services.indexar import vectorstore, gerar_id_unico
except ImportError:
    # Fallback para execução direta
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from app.services.indexar import vectorstore, gerar_id_unico

from langchain_core.documents import Document

class LeiEnriquecidaIndexer:
    def __init__(self):
        self.vectorstore = vectorstore
        
    def carregar_leis_enriquecidas(self, arquivo_path: str) -> List[Dict[str, Any]]:
        """Carrega as leis enriquecidas do arquivo JSON"""
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                leis = json.load(f)
            print(f"✅ {len(leis)} leis carregadas de {arquivo_path}")
            return leis
        except Exception as e:
            print(f"❌ Erro ao carregar leis: {e}")
            return []
    
    def preparar_documentos(self, leis: List[Dict[str, Any]]) -> List[Document]:
        """Prepara os documentos para indexação no Pinecone"""
        documentos = []
        
        for lei in leis:
            try:
                # Criar metadados enriquecidos
                metadata = {
                    "titulo": lei.get("titulo", ""),
                    "descricao": lei.get("descricao", ""),
                    "fonte": lei.get("fonte", "PDF_SIMULADO"),
                    "tipo": "lei_ambiental",
                    "categoria": "legislacao_tocantins",
                    "tamanho_original": lei.get("tamanho_original", 0),
                    "tamanho_enriquecido": lei.get("tamanho_enriquecido", 0),
                    "data_processamento": lei.get("data_processamento", ""),
                    "data_indexacao": datetime.now().isoformat()
                }
                
                # Criar documento
                documento = Document(
                    page_content=lei.get("conteudo", ""),
                    metadata=metadata
                )
                
                documentos.append(documento)
                
            except Exception as e:
                print(f"❌ Erro ao preparar documento para lei {lei.get('titulo', 'desconhecida')}: {e}")
                continue
        
        print(f"✅ {len(documentos)} documentos preparados para indexação")
        return documentos
    
    def indexar_documentos(self, documentos: List[Document]) -> bool:
        """Indexa os documentos no Pinecone"""
        try:
            print("🔄 Iniciando indexação no Pinecone...")
            
            # Gerar IDs únicos para cada documento baseado no conteúdo
            ids = [gerar_id_unico(doc.page_content) for doc in documentos]
            
            # Indexar no Pinecone
            self.vectorstore.add_documents(documentos, ids=ids)
            
            print(f"✅ {len(documentos)} documentos indexados com sucesso no Pinecone!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao indexar documentos: {e}")
            return False
    
    def processar_arquivo(self, arquivo_path: str) -> Dict[str, Any]:
        """Processa um arquivo de leis enriquecidas completo"""
        print(f"🚀 Iniciando processamento de {arquivo_path}")
        
        # Carregar leis
        leis = self.carregar_leis_enriquecidas(arquivo_path)
        if not leis:
            return {"sucesso": False, "erro": "Nenhuma lei carregada"}
        
        # Preparar documentos
        documentos = self.preparar_documentos(leis)
        if not documentos:
            return {"sucesso": False, "erro": "Nenhum documento preparado"}
        
        # Indexar
        sucesso_indexacao = self.indexar_documentos(documentos)
        
        resultado = {
            "sucesso": sucesso_indexacao,
            "total_leis": len(leis),
            "total_documentos": len(documentos),
            "arquivo_processado": arquivo_path,
            "data_processamento": datetime.now().isoformat()
        }
        
        return resultado

def main():
    """Função principal"""
    print("=== INDEXADOR DE LEIS AMBIENTAIS ENRIQUECIDAS ===\n")
    
    # Encontrar o arquivo mais recente de leis enriquecidas
    tests_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests")
    arquivos_enriquecidos = [f for f in os.listdir(tests_dir) if f.startswith("leis_enriquecidas_") and f.endswith(".json")]
    
    if not arquivos_enriquecidos:
        print("❌ Nenhum arquivo de leis enriquecidas encontrado!")
        return
    
    # Usar o arquivo mais recente
    arquivo_mais_recente = sorted(arquivos_enriquecidos)[-1]
    arquivo_path = os.path.join(tests_dir, arquivo_mais_recente)
    
    print(f"📁 Arquivo selecionado: {arquivo_mais_recente}")
    
    # Processar
    indexer = LeiEnriquecidaIndexer()
    resultado = indexer.processar_arquivo(arquivo_path)
    
    # Exibir resultado
    print("\n=== RESULTADO FINAL ===")
    if resultado["sucesso"]:
        print("🎉 Indexação concluída com sucesso!")
        print(f"📊 Total de leis processadas: {resultado['total_leis']}")
        print(f"📊 Total de documentos indexados: {resultado['total_documentos']}")
    else:
        print("❌ Falha na indexação!")
        if "erro" in resultado:
            print(f"Erro: {resultado['erro']}")
    
    print(f"📅 Data do processamento: {resultado['data_processamento']}")

if __name__ == "__main__":
    main()