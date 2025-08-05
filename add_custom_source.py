"""
Script para adicionar facilmente novas fontes personalizadas
Permite que o usuário adicione documentos de qualquer fonte
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_source_indexer import MultiSourceIndexer

def parse_arguments():
    """Analisa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Adicionar fonte personalizada de dados')
    
    parser.add_argument('--source', '-s', type=str, required=True,
                        help='Nome da fonte (ex: "Ministério do Meio Ambiente")')
    
    parser.add_argument('--file', '-f', type=str, required=False,
                        help='Arquivo JSON com documentos para indexar')
    
    parser.add_argument('--url', '-u', type=str, required=False,
                        help='URL para coletar dados (PDF ou HTML)')
    
    parser.add_argument('--text', '-t', type=str, required=False,
                        help='Texto direto para indexar')
    
    parser.add_argument('--output', '-o', type=str, default='custom_source_data.json',
                        help='Arquivo de saída para salvar os dados')
    
    return parser.parse_args()

def add_from_file(source_name, filename, output_file):
    """Adiciona documentos de um arquivo JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            documents = json.load(f)
            
        # Verifica se o formato está correto
        if not isinstance(documents, list):
            print("Erro: O arquivo deve conter uma lista de documentos")
            return
            
        # Adiciona metadados necessários
        for doc in documents:
            if 'text' not in doc:
                print(f"Aviso: Documento sem texto será ignorado: {doc}")
                continue
                
            doc['source'] = source_name
            if 'collected_at' not in doc:
                doc['collected_at'] = datetime.now().isoformat()
                
        # Salva backup
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
            
        # Indexa
        indexer = MultiSourceIndexer()
        indexer.add_custom_source(source_name, documents)
        
        print(f"Adicionados {len(documents)} documentos da fonte {source_name}")
        
    except Exception as e:
        print(f"Erro ao processar arquivo {filename}: {e}")

def add_from_url(source_name, url, output_file):
    """Adiciona documento de uma URL"""
    import requests
    import pypdf
    import io
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        
        text = ""
        doc_type = ""
        
        # Determina o tipo de documento
        if url.lower().endswith('.pdf'):
            # Extrai texto do PDF
            pdf_file = io.BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_file)
            
            for page in reader.pages:
                text += page.extract_text() or ""
                
            doc_type = 'pdf'
            
        else:
            # Assume que é HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            doc_type = 'html'
            
        if not text:
            print(f"Aviso: Nenhum texto extraído de {url}")
            return
            
        # Cria documento
        document = {
            'source': source_name,
            'url': url,
            'text': text,
            'type': doc_type,
            'collected_at': datetime.now().isoformat()
        }
        
        # Salva backup
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([document], f, ensure_ascii=False, indent=2)
            
        # Indexa
        indexer = MultiSourceIndexer()
        indexer.add_custom_source(source_name, [document])
        
        print(f"Adicionado documento de {url} da fonte {source_name}")
        
    except Exception as e:
        print(f"Erro ao processar URL {url}: {e}")

def add_from_text(source_name, text, output_file):
    """Adiciona documento de um texto direto"""
    try:
        # Cria documento
        document = {
            'source': source_name,
            'url': 'manual_input',
            'text': text,
            'type': 'text',
            'collected_at': datetime.now().isoformat()
        }
        
        # Salva backup
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([document], f, ensure_ascii=False, indent=2)
            
        # Indexa
        indexer = MultiSourceIndexer()
        indexer.add_custom_source(source_name, [document])
        
        print(f"Adicionado texto manual da fonte {source_name}")
        
    except Exception as e:
        print(f"Erro ao processar texto: {e}")

def main():
    """Função principal"""
    args = parse_arguments()
    
    if not any([args.file, args.url, args.text]):
        print("Erro: Você deve fornecer pelo menos um dos seguintes: --file, --url ou --text")
        return
        
    if args.file:
        add_from_file(args.source, args.file, args.output)
        
    if args.url:
        add_from_url(args.source, args.url, args.output)
        
    if args.text:
        add_from_text(args.source, args.text, args.output)

if __name__ == "__main__":
    main()