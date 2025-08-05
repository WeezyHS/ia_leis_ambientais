"""
Sistema modular para coleta de dados de múltiplas fontes
Permite adicionar facilmente novos scrapers para diferentes sites governamentais
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pypdf
import io
from tqdm import tqdm
import json
from datetime import datetime

class BaseScraper(ABC):
    """Classe base para todos os scrapers"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.driver = None
        
    def setup_driver(self, headless: bool = True):
        """Configura o driver do Selenium"""
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Edge(
            service=EdgeService(executable_path="msedgedriver.exe"), 
            options=options
        )
        
    def cleanup_driver(self):
        """Limpa o driver"""
        if self.driver:
            self.driver.quit()
            
    @abstractmethod
    def extract_documents(self) -> List[Dict]:
        """Método abstrato para extrair documentos"""
        pass
        
    @abstractmethod
    def is_relevant_document(self, text: str) -> bool:
        """Método abstrato para verificar se o documento é relevante"""
        pass

class TocantinsAssembleiaScraper(BaseScraper):
    """Scraper para a Assembleia Legislativa do Tocantins (fonte atual)"""
    
    def __init__(self):
        super().__init__("Assembleia TO", "https://www.al.to.leg.br/legislacaoEstadual")
        
    def extract_documents(self) -> List[Dict]:
        """Extrai documentos da Assembleia do Tocantins"""
        documents = []
        self.setup_driver()
        
        try:
            for page in range(1, 4):  # Primeiras 3 páginas para teste
                url = f"{self.base_url}?pagPaginaAtual={page}"
                print(f"Coletando página {page}: {url}")
                
                self.driver.get(url)
                time.sleep(5)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Busca links de PDF
                for link in soup.find_all('a', href=True):
                    if link['href'].startswith('/arquivo/'):
                        pdf_url = requests.compat.urljoin(self.base_url, link['href'])
                        text = self._extract_pdf_text(pdf_url)
                        
                        if text and self.is_relevant_document(text):
                            documents.append({
                                'source': self.name,
                                'url': pdf_url,
                                'text': text,
                                'type': 'pdf',
                                'collected_at': datetime.now().isoformat()
                            })
                            
                time.sleep(2)
                
        finally:
            self.cleanup_driver()
            
        return documents
        
    def _extract_pdf_text(self, pdf_url: str) -> Optional[str]:
        """Extrai texto de um PDF"""
        try:
            response = requests.get(pdf_url, timeout=20)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                
            return text
        except Exception as e:
            print(f"Erro ao extrair PDF {pdf_url}: {e}")
            return None
            
    def is_relevant_document(self, text: str) -> bool:
        """Verifica se é documento ambiental relevante"""
        keywords = [
            "meio ambiente", "ambiental", "ecologia", "sustentabilidade",
            "recursos hídricos", "fauna", "flora", "biodiversidade",
            "poluição", "resíduos", "licenciamento ambiental",
            "impacto ambiental", "gestão ambiental"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

class PlanaltoScraper(BaseScraper):
    """Scraper para leis federais do Planalto"""
    
    def __init__(self):
        super().__init__("Planalto Federal", "https://www.planalto.gov.br")
        
    def extract_documents(self) -> List[Dict]:
        """Extrai leis federais ambientais do Planalto"""
        documents = []
        
        # URLs específicas de leis ambientais importantes
        environmental_laws = [
            "https://www.planalto.gov.br/ccivil_03/leis/l6938.htm",  # Política Nacional do Meio Ambiente
            "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12305.htm",  # Política Nacional de Resíduos Sólidos
            "https://www.planalto.gov.br/ccivil_03/leis/l9985.htm",  # Sistema Nacional de Unidades de Conservação
            "https://www.planalto.gov.br/ccivil_03/leis/l12651.htm",  # Código Florestal
            "https://www.planalto.gov.br/ccivil_03/leis/l9433.htm",  # Política Nacional de Recursos Hídricos
        ]
        
        for url in environmental_laws:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                
                if self.is_relevant_document(text):
                    documents.append({
                        'source': self.name,
                        'url': url,
                        'text': text,
                        'type': 'html',
                        'collected_at': datetime.now().isoformat()
                    })
                    
                time.sleep(1)  # Respeita o servidor
                
            except Exception as e:
                print(f"Erro ao coletar {url}: {e}")
                
        return documents
        
    def is_relevant_document(self, text: str) -> bool:
        """Verifica se é documento ambiental relevante"""
        return len(text) > 1000  # Leis federais são sempre relevantes se têm conteúdo

class IbamaScraper(BaseScraper):
    """Scraper para normativas do IBAMA"""
    
    def __init__(self):
        super().__init__("IBAMA", "https://www.ibama.gov.br")
        
    def extract_documents(self) -> List[Dict]:
        """Extrai normativas do IBAMA"""
        documents = []
        
        # URLs de seções importantes do IBAMA
        ibama_sections = [
            "https://www.ibama.gov.br/legislacao",
            "https://www.ibama.gov.br/phocadownload/legislacao/instrucoes-normativas",
        ]
        
        for url in ibama_sections:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Busca links para documentos
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                            full_url = requests.compat.urljoin(url, href)
                            
                            if href.endswith('.pdf'):
                                text = self._extract_pdf_text(full_url)
                            else:
                                continue  # Por enquanto, só PDFs
                                
                            if text and self.is_relevant_document(text):
                                documents.append({
                                    'source': self.name,
                                    'url': full_url,
                                    'text': text,
                                    'type': 'pdf',
                                    'collected_at': datetime.now().isoformat()
                                })
                                
                time.sleep(2)
                
            except Exception as e:
                print(f"Erro ao coletar IBAMA {url}: {e}")
                
        return documents
        
    def _extract_pdf_text(self, pdf_url: str) -> Optional[str]:
        """Extrai texto de um PDF"""
        try:
            response = requests.get(pdf_url, timeout=20)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                
            return text
        except Exception as e:
            print(f"Erro ao extrair PDF {pdf_url}: {e}")
            return None
            
    def is_relevant_document(self, text: str) -> bool:
        """Verifica se é documento ambiental relevante"""
        keywords = [
            "licenciamento", "fauna", "flora", "conservação",
            "fiscalização", "multa", "infração", "ambiental"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

class MultiSourceCollector:
    """Coordenador para coleta de múltiplas fontes"""
    
    def __init__(self):
        self.scrapers = [
            TocantinsAssembleiaScraper(),
            PlanaltoScraper(),
            IbamaScraper(),
        ]
        
    def add_scraper(self, scraper: BaseScraper):
        """Adiciona um novo scraper"""
        self.scrapers.append(scraper)
        
    def collect_all_sources(self) -> List[Dict]:
        """Coleta dados de todas as fontes"""
        all_documents = []
        
        for scraper in self.scrapers:
            print(f"\n=== Coletando de: {scraper.name} ===")
            try:
                documents = scraper.extract_documents()
                all_documents.extend(documents)
                print(f"Coletados {len(documents)} documentos de {scraper.name}")
            except Exception as e:
                print(f"Erro ao coletar de {scraper.name}: {e}")
                
        return all_documents
        
    def save_to_file(self, documents: List[Dict], filename: str = "multi_source_data.json"):
        """Salva os documentos coletados em arquivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos em {filename}")

if __name__ == "__main__":
    collector = MultiSourceCollector()
    documents = collector.collect_all_sources()
    collector.save_to_file(documents)
    print(f"\nTotal de documentos coletados: {len(documents)}")