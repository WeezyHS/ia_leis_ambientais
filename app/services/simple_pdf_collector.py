"""
Coletor simplificado de PDFs sem Selenium
Usa apenas requests para acessar as páginas e baixar PDFs
"""

import requests
import json
import io
import re
from typing import List, Dict
from bs4 import BeautifulSoup
import pypdf
from app.services.leis_html_service import eh_lei_ambiental, normalizar_texto

class SimplePDFCollector:
    """Coletor simplificado que não usa Selenium"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_content(self, url: str) -> str:
        """Obtém conteúdo HTML de uma página"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            return ""
    
    def extract_laws_from_html(self, html_content: str, page_url: str) -> List[Dict]:
        """Extrai informações das leis de uma página HTML"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        leis = []
        
        # Procura por elementos que contêm leis
        # Adapte estes seletores conforme a estrutura real do site
        lei_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'lei|norma|legislacao', re.I))
        
        if not lei_elements:
            # Fallback: procura por links que contenham "lei" ou "pdf"
            lei_elements = soup.find_all('a', href=re.compile(r'(lei|pdf)', re.I))
        
        for element in lei_elements:
            try:
                # Extrai título
                titulo_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b']) or element
                titulo = normalizar_texto(titulo_elem.get_text())
                
                if not titulo or len(titulo) < 10:
                    continue
                
                # Verifica se é lei ambiental
                if not eh_lei_ambiental(titulo):
                    continue
                
                # Procura por links de PDF
                pdf_links = []
                for link in element.find_all('a', href=True):
                    href = link['href']
                    if href.lower().endswith('.pdf') or 'pdf' in href.lower():
                        if not href.startswith('http'):
                            href = f"https://www.al.to.leg.br{href}"
                        pdf_links.append(href)
                
                # Extrai descrição
                descricao = ""
                text_content = element.get_text()
                if len(text_content) > len(titulo):
                    descricao = normalizar_texto(text_content[len(titulo):])[:500]
                
                lei_info = {
                    'titulo': titulo,
                    'descricao': descricao,
                    'pdf_links': pdf_links,
                    'page_url': page_url,
                    'conteudo': text_content[:1000]  # Conteúdo inicial
                }
                
                leis.append(lei_info)
                
            except Exception as e:
                print(f"Erro ao processar elemento: {e}")
                continue
        
        return leis
    
    def download_and_extract_pdf(self, pdf_url: str) -> str:
        """Baixa e extrai texto de um PDF"""
        try:
            print(f"Baixando PDF: {pdf_url}")
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Extrai texto do PDF
            pdf_file = io.BytesIO(response.content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            texto_completo = ""
            for page in pdf_reader.pages:
                texto_completo += page.extract_text() + "\n"
            
            return normalizar_texto(texto_completo)
            
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_url}: {e}")
            return ""
    
    def collect_laws_from_page(self, page_num: int) -> List[Dict]:
        """Coleta leis de uma página específica"""
        url = f"https://www.al.to.leg.br/legislacaoEstadual?page={page_num}"
        print(f"Processando página {page_num}: {url}")
        
        html_content = self.get_page_content(url)
        if not html_content:
            return []
        
        leis = self.extract_laws_from_html(html_content, url)
        
        # Processa PDFs para cada lei
        for lei in leis:
            if lei['pdf_links']:
                # Usa o primeiro PDF encontrado
                pdf_url = lei['pdf_links'][0]
                pdf_content = self.download_and_extract_pdf(pdf_url)
                
                if pdf_content:
                    lei['conteudo'] = pdf_content
                    lei['fonte'] = 'PDF'
                else:
                    lei['fonte'] = 'HTML'
            else:
                lei['fonte'] = 'HTML'
        
        return leis
    
    def collect_all_laws(self, max_pages: int = 250) -> List[Dict]:
        """Coleta todas as leis ambientais"""
        print(f"=== INICIANDO COLETA DE LEIS AMBIENTAIS ===")
        print(f"Páginas a processar: {max_pages}")
        
        todas_leis = []
        
        for page_num in range(1, max_pages + 1):
            try:
                leis_pagina = self.collect_laws_from_page(page_num)
                
                if leis_pagina:
                    todas_leis.extend(leis_pagina)
                    print(f"Página {page_num}: {len(leis_pagina)} leis ambientais encontradas")
                else:
                    print(f"Página {page_num}: Nenhuma lei ambiental encontrada")
                
                # Pausa entre requisições
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro na página {page_num}: {e}")
                continue
        
        print(f"\n=== COLETA FINALIZADA ===")
        print(f"Total de leis ambientais coletadas: {len(todas_leis)}")
        
        return todas_leis

def test_simple_collector():
    """Testa o coletor simplificado"""
    collector = SimplePDFCollector()
    
    # Testa com 2 páginas
    leis = collector.collect_all_laws(max_pages=2)
    
    # Salva resultado
    with open("tests/leis_simple_test.json", "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)
    
    print(f"Teste concluído. {len(leis)} leis salvas em tests/leis_simple_test.json")
    
    return leis

if __name__ == "__main__":
    test_simple_collector()