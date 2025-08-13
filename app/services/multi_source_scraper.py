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

class CONAMAScraper(BaseScraper):
    """Scraper para resoluções do CONAMA"""
    
    def __init__(self):
        super().__init__("CONAMA", "https://conama.mma.gov.br")
        
    def extract_documents(self) -> List[Dict]:
        """Extrai resoluções do CONAMA usando dados já coletados"""
        documents = []
        
        # Carrega dados já coletados do CONAMA
        conama_files = [
            "conama_data_20250811_111053.json",
            "conama_data_20250805_150217.json",
            "conama_data_20250805_145759.json"
        ]
        
        for filename in conama_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        conama_data = json.load(f)
                    
                    for doc in conama_data:
                        # Verifica se tem conteúdo útil
                        if doc.get('text') and doc['text'] not in ['Download', '']:
                            documents.append({
                                'source': 'CONAMA',
                                'url': doc['url'],
                                'text': doc['text'],
                                'type': 'ato_normativo',
                                'collected_at': doc.get('collected_at', datetime.now().isoformat()),
                                'ano': doc.get('ano'),
                                'tipo_ato': doc.get('tipo_ato'),
                                'status': doc.get('status', 'vigente')
                            })
                            
                except Exception as e:
                    print(f"Erro ao carregar {filename}: {e}")
                    
        return documents
        
    def is_relevant_document(self, text: str) -> bool:
        """Documentos do CONAMA são sempre relevantes"""
        return len(text) > 10  # Qualquer conteúdo mínimo

class COEMAScraper(BaseScraper):
    """Scraper para dados do COEMA e CERH do Tocantins"""
    
    def __init__(self):
        super().__init__("COEMA/CERH", "https://www.to.gov.br/semarh")
        self.visited_urls = set()
        
    def extract_documents(self) -> List[Dict]:
        """Extrai documentos do COEMA e CERH navegando por múltiplas seções"""
        documents = []
        
        # URLs principais para explorar
        main_urls = [
            "https://www.to.gov.br/semarh/conselhos/34qnn4fkmozg",
            "https://www.to.gov.br/semarh/legislacao",
            "https://www.to.gov.br/semarh/portarias",
            "https://www.to.gov.br/semarh/resolucoes-e-outros-atos",
            "https://www.to.gov.br/semarh/leis",
            "https://www.to.gov.br/semarh/decretos",
            "https://www.to.gov.br/semarh/consultas-publicas",
            "https://www.to.gov.br/semarh/editais",
            "https://www.to.gov.br/semarh/recursos-hidricos",
            "https://www.to.gov.br/semarh/meio-ambiente",
            "https://www.to.gov.br/semarh/unidades-colegiadas"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for url in main_urls:
            try:
                print(f"Explorando: {url}")
                docs_from_url = self._extract_from_url(url, headers)
                documents.extend(docs_from_url)
                print(f"Coletados {len(docs_from_url)} documentos de {url}")
                
                # Pequena pausa entre requisições
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
                continue
        
        # Buscar por mais URLs relacionadas
        additional_docs = self._search_additional_pages(headers)
        documents.extend(additional_docs)
        
        print(f"Total de documentos coletados: {len(documents)}")
        return documents
    
    def _extract_from_url(self, url: str, headers: dict) -> List[Dict]:
        """Extrai documentos de uma URL específica"""
        documents = []
        
        if url in self.visited_urls:
            return documents
            
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Buscar links diretos para documentos
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                
                if not link_text or len(link_text) < 3:
                    continue
                
                # Construir URL completa
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = "https://www.to.gov.br" + href
                else:
                    full_url = requests.compat.urljoin(url, href)
                
                # Verificar se é documento relevante
                if self._is_document_link(href, link_text):
                    doc = self._process_document_link(full_url, link_text, headers)
                    if doc:
                        documents.append(doc)
                
                # Verificar se é página com mais conteúdo para explorar
                elif self._is_relevant_page_link(href, link_text):
                    if full_url not in self.visited_urls and len(self.visited_urls) < 50:  # Limite para evitar loop infinito
                        sub_docs = self._extract_from_url(full_url, headers)
                        documents.extend(sub_docs)
            
            # 2. Extrair conteúdo da própria página se relevante
            page_content = soup.get_text(separator='\n', strip=True)
            if self.is_relevant_document(page_content) and len(page_content) > 200:
                title = self._extract_page_title(soup, url)
                documents.append({
                    'source': self.name,
                    'url': url,
                    'text': page_content,
                    'title': title,
                    'type': self._identify_document_type(title, page_content),
                    'collected_at': datetime.now().isoformat(),
                    'conselho': self._identify_council(page_content, title)
                })
                
        except Exception as e:
            print(f"Erro ao extrair de {url}: {e}")
            
        return documents
    
    def _is_document_link(self, href: str, link_text: str) -> bool:
        """Verifica se o link aponta para um documento"""
        href_lower = href.lower()
        text_lower = link_text.lower()
        
        # Extensões de arquivo
        if any(ext in href_lower for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
            return True
            
        # Palavras-chave no texto do link
        keywords = [
            'resolução', 'resolucao', 'portaria', 'deliberação', 'deliberacao',
            'ata', 'regimento', 'lei', 'decreto', 'normativa', 'instrução',
            'instrucao', 'circular', 'parecer', 'relatório', 'relatorio'
        ]
        
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_relevant_page_link(self, href: str, link_text: str) -> bool:
        """Verifica se o link aponta para uma página relevante para explorar"""
        href_lower = href.lower()
        text_lower = link_text.lower()
        
        # Evitar links externos ou irrelevantes
        if any(domain in href_lower for domain in ['facebook', 'twitter', 'instagram', 'youtube', 'mailto:', 'tel:']):
            return False
            
        # Páginas relevantes
        relevant_terms = [
            'coema', 'cerh', 'conselho', 'legislacao', 'portaria', 'resolucao',
            'meio-ambiente', 'recursos-hidricos', 'ambiental', 'hidrico',
            'deliberacao', 'ata', 'regimento', 'normativa'
        ]
        
        return any(term in href_lower or term in text_lower for term in relevant_terms)
    
    def _process_document_link(self, url: str, title: str, headers: dict) -> Optional[Dict]:
        """Processa um link de documento"""
        try:
            text = self._extract_document_text(url, url)
            
            if text and self.is_relevant_document(text):
                return {
                    'source': self.name,
                    'url': url,
                    'text': text,
                    'title': title,
                    'type': self._identify_document_type(title, text),
                    'collected_at': datetime.now().isoformat(),
                    'conselho': self._identify_council(text, title)
                }
        except Exception as e:
            print(f"Erro ao processar documento {url}: {e}")
            
        return None
    
    def _extract_page_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extrai o título da página"""
        # Tentar diferentes elementos para o título
        title_selectors = ['h1', 'h2', '.page-title', '.title', 'title']
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        # Fallback para URL
        return url.split('/')[-1].replace('-', ' ').title()
    
    def _search_additional_pages(self, headers: dict) -> List[Dict]:
        """Busca por páginas adicionais usando termos específicos"""
        documents = []
        
        # Termos para buscar páginas específicas
        search_terms = [
            'coema-conselho-estadual-meio-ambiente',
            'cerh-conselho-estadual-recursos-hidricos',
            'resolucoes-coema',
            'portarias-semarh',
            'deliberacoes-cerh',
            'atas-coema',
            'regimento-interno'
        ]
        
        for term in search_terms:
            try:
                search_url = f"https://www.to.gov.br/semarh/{term}"
                if search_url not in self.visited_urls:
                    docs = self._extract_from_url(search_url, headers)
                    documents.extend(docs)
                    time.sleep(1)
            except Exception as e:
                continue
                
        return documents
        
    def _extract_document_text(self, url: str, href: str) -> Optional[str]:
        """Extrai texto de um documento"""
        try:
            if href.lower().endswith('.pdf'):
                return self._extract_pdf_text(url)
            else:
                # Para outros tipos, tenta extrair como HTML
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Erro ao extrair documento {url}: {e}")
            return None
            
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
            
    def _identify_document_type(self, title: str, text: str) -> str:
        """Identifica o tipo de documento"""
        title_lower = title.lower()
        text_lower = text.lower()
        
        if any(word in title_lower for word in ['resolução', 'resolucao']):
            return 'resolucao'
        elif any(word in title_lower for word in ['portaria']):
            return 'portaria'
        elif any(word in title_lower for word in ['deliberação', 'deliberacao']):
            return 'deliberacao'
        elif any(word in title_lower for word in ['ata']):
            return 'ata'
        elif any(word in title_lower for word in ['regimento']):
            return 'regimento'
        elif any(word in title_lower for word in ['lei']):
            return 'lei'
        else:
            return 'documento'
            
    def _identify_council(self, text: str, title: str) -> str:
        """Identifica qual conselho (COEMA ou CERH)"""
        combined_text = (text + " " + title).lower()
        
        if 'coema' in combined_text or 'meio ambiente' in combined_text:
            return 'COEMA'
        elif 'cerh' in combined_text or 'recursos hídricos' in combined_text or 'água' in combined_text:
            return 'CERH'
        else:
            return 'SEMARH'
            
    def is_relevant_document(self, text: str) -> bool:
        """Verifica se é documento relevante do COEMA/CERH"""
        if len(text) < 50:  # Muito pouco conteúdo
            return False
            
        keywords = [
            "coema", "cerh", "meio ambiente", "recursos hídricos", "água",
            "licenciamento", "ambiental", "conselho", "deliberação", "resolução",
            "portaria", "semarh", "tocantins", "gestão ambiental", "poluição",
            "conservação", "sustentabilidade", "biodiversidade", "fauna", "flora"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

class ABNTScraper(BaseScraper):
    """Scraper para normas da ABNT - apenas normas vigentes"""
    
    def __init__(self):
        super().__init__("ABNT", "https://www.abntcatalogo.com.br")
        self.environmental_terms = [
            "ambiental", "meio ambiente", "poluição", "resíduos", "água", "ar",
            "solo", "sustentabilidade", "ecologia", "biodiversidade", "clima",
            "emissões", "efluentes", "gestão ambiental", "ISO 14001", "licenciamento"
        ]
        
    def extract_documents(self) -> List[Dict]:
        """Extrai normas da ABNT que estão vigentes"""
        documents = []
        
        try:
            # Configura o driver
            self.setup_driver()
            
            # Acessa a página principal do catálogo
            print("Acessando o catálogo ABNT...")
            self.driver.get("https://www.abntcatalogo.com.br/pav.aspx")
            time.sleep(5)
            
            for term in self.environmental_terms:
                try:
                    print(f"Buscando normas ABNT para: {term}")
                    
                    # Aguardar a página carregar completamente
                    wait = WebDriverWait(self.driver, 15)
                    wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphPagina_txtNM_Palavra")))
                    
                    # Localizar campo de pesquisa por palavra-chave
                    search_field = self.driver.find_element(By.ID, "ctl00_cphPagina_txtNM_Palavra")
                    
                    # Garantir que apenas normas ABNT vigentes sejam buscadas
                    # Verificar se checkbox ABNT está marcado
                    abnt_checkbox = self.driver.find_element(By.ID, "cphPagina_chkNM_ABNT")
                    if not abnt_checkbox.is_selected():
                        abnt_checkbox.click()
                        time.sleep(1)
                    
                    # Garantir que apenas normas ativas sejam buscadas
                    active_checkbox = self.driver.find_element(By.ID, "cphPagina_chkNM_Ativo")
                    if not active_checkbox.is_selected():
                        active_checkbox.click()
                        time.sleep(1)
                    
                    # Desmarcar normas canceladas se estiver marcado
                    cancelled_checkbox = self.driver.find_element(By.ID, "cphPagina_chkNM_Cancelada")
                    if cancelled_checkbox.is_selected():
                        cancelled_checkbox.click()
                        time.sleep(1)
                    
                    # Limpar campo e inserir termo
                    search_field.clear()
                    time.sleep(1)
                    search_field.send_keys(term)
                    time.sleep(1)
                    
                    # Clicar no botão de busca
                    search_button = self.driver.find_element(By.ID, "cphPagina_cmdNM_Buscar")
                    search_button.click()
                    
                    # Aguardar resultados
                    time.sleep(5)
                    
                    # Extrair resultados
                    standards = self._extract_search_results()
                    documents.extend(standards)
                    
                    print(f"Encontradas {len(standards)} normas para o termo '{term}'")
                    
                    # Voltar para a página de busca para próximo termo
                    self.driver.get("https://www.abntcatalogo.com.br/pav.aspx")
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"Erro ao buscar '{term}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro geral no scraper ABNT: {e}")
        finally:
            self.cleanup_driver()
            
        # Remover duplicatas
        unique_documents = []
        seen_codes = set()
        
        for doc in documents:
            code = doc.get('codigo', '')
            if code and code not in seen_codes:
                unique_documents.append(doc)
                seen_codes.add(code)
                
        return unique_documents
        
    def _extract_search_results(self) -> List[Dict]:
        """Extrai os resultados da busca"""
        standards = []
        
        try:
            # Aguardar carregamento dos resultados
            time.sleep(3)
            
            # Procurar por tabelas de resultados ou listas
            result_tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            
            # Se encontrou tabelas, processar
            for table in result_tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows[1:]:  # Pular cabeçalho
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            standard_data = self._extract_standard_from_row(cells)
                            if standard_data and self.is_relevant_document(standard_data.get('titulo', '') + ' ' + standard_data.get('resumo', '')):
                                standards.append(standard_data)
                    except Exception as e:
                        continue
            
            # Se não encontrou resultados estruturados, tentar extrair do HTML
            if not standards:
                standards = self._extract_from_page_content()
                
        except Exception as e:
            print(f"Erro ao extrair resultados: {e}")
        
        return standards
        
    def _extract_standard_from_row(self, cells) -> Optional[Dict]:
        """Extrai dados de uma linha de tabela"""
        try:
            # Assumindo estrutura típica: código, título, status, etc.
            codigo = cells[0].text.strip() if len(cells) > 0 else "N/A"
            titulo = cells[1].text.strip() if len(cells) > 1 else "N/A"
            status = cells[2].text.strip() if len(cells) > 2 else "Vigente"
            
            # Verificar se é vigente
            if "cancelad" in status.lower() or "withdraw" in status.lower() or "inativ" in status.lower():
                return None
            
            return {
                'source': self.name,
                'url': self.driver.current_url,
                'codigo': codigo,
                'titulo': titulo,
                'status': status,
                'text': titulo,
                'type': 'norma_abnt',
                'collected_at': datetime.now().isoformat(),
                'resumo': titulo,
                'escopo': "",
                'comite': ""
            }
            
        except Exception as e:
            return None
            
    def _extract_from_page_content(self) -> List[Dict]:
        """Extrai normas do conteúdo da página quando não há estrutura clara"""
        standards = []
        
        try:
            page_text = self.driver.page_source
            
            # Procurar por padrões de normas ABNT
            import re
            
            # Padrão para normas ABNT NBR
            nbr_pattern = r'(ABNT\s+NBR\s+\d+(?:-\d+)?(?::\d{4})?)'  
            matches = re.findall(nbr_pattern, page_text, re.IGNORECASE)
            
            for match in matches:
                # Criar entrada básica para cada norma encontrada
                if self.is_relevant_document(match):
                    standard = {
                        'source': self.name,
                        'url': self.driver.current_url,
                        'codigo': match,
                        'titulo': f"Norma {match}",
                        'status': "Vigente",
                        'text': f"Norma técnica {match} da ABNT",
                        'type': 'norma_abnt',
                        'collected_at': datetime.now().isoformat(),
                        'resumo': f"Norma técnica {match} da ABNT",
                        'escopo': "",
                        'comite': ""
                    }
                    standards.append(standard)
            
        except Exception as e:
            print(f"Erro ao extrair do conteúdo da página: {e}")
        
        return standards
            
    def is_relevant_document(self, text: str) -> bool:
        """Verifica se é norma ambiental relevante"""
        if len(text) < 10:  # Muito pouco conteúdo
            return False
            
        environmental_keywords = [
            "ambiental", "meio ambiente", "poluição", "resíduos",
            "água", "ar", "solo", "gestão ambiental", "sustentabilidade",
            "emissões", "efluentes", "tratamento", "qualidade ambiental",
            "impacto ambiental", "conservação", "preservação",
            "saneamento", "efluente", "atmosfera", "ruído", "vibração",
            "ecologia", "biodiversidade", "clima", "iso 14001", "licenciamento"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in environmental_keywords)

class MultiSourceCollector:
    """Coordenador para coleta de múltiplas fontes"""
    
    def __init__(self):
        self.scrapers = [
            TocantinsAssembleiaScraper(),
            PlanaltoScraper(),
            IbamaScraper(),
            CONAMAScraper(),
            COEMAScraper(),
            ABNTScraper(),
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