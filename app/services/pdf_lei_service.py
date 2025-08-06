"""
Serviço para coleta e processamento de PDFs das leis ambientais
do site da Assembleia Legislativa do Tocantins
"""

import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import pypdf
import io
from typing import List, Dict, Optional
import re
from app.services.leis_html_service import PALAVRAS_CHAVE_EXATAS, SIGLAS_MAIUSCULAS, contem_palavra_chave

class PDFLeiCollector:
    """Coletor de PDFs das leis ambientais"""
    
    def __init__(self):
        self.base_url = "https://www.al.to.leg.br/legislacaoEstadual"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def setup_driver(self):
        """Configura o driver do Selenium com webdriver-manager"""
        # Tenta Chrome primeiro (mais estável)
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            print("Configurando Google Chrome...")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
            
        except Exception as e:
            print(f"Chrome não disponível: {e}")
            
        # Fallback para Edge
        try:
            options = EdgeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            print("Configurando Microsoft Edge...")
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
            
        except Exception as e:
            print(f"Edge não disponível: {e}")
            
        # Se nenhum funcionar, levanta erro
        raise WebDriverException("Nenhum driver de navegador disponível (Chrome ou Edge)")
    
    def extract_pdf_links_from_page(self, html_content: str) -> List[Dict]:
        """Extrai links de PDFs e informações das leis de uma página"""
        soup = BeautifulSoup(html_content, "html.parser")
        leis_com_pdf = []
        
        # Procura por blocos de leis
        blocos = soup.find_all("div", class_="row")
        
        for bloco in blocos:
            try:
                # Extrai informações básicas da lei
                colunas = bloco.find_all("div", class_="col-12")
                if len(colunas) < 3:
                    continue
                
                titulo_tag = colunas[0].find("h4")
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""
                
                descricao_tag = colunas[1].find("strong")
                descricao = descricao_tag.get_text(strip=True) if descricao_tag else ""
                
                conteudo_preview = colunas[2].get_text(separator="\n", strip=True)
                
                # Verifica se é uma lei ambiental
                texto_completo = f"{titulo}\n{descricao}\n{conteudo_preview}"
                if not contem_palavra_chave(texto_completo):
                    continue
                
                # Procura por links de PDF
                pdf_links = []
                
                # Busca links diretos para PDF
                for link in bloco.find_all("a", href=True):
                    href = link.get("href", "")
                    if href.endswith(".pdf") or "pdf" in href.lower():
                        if href.startswith("/"):
                            href = "https://www.al.to.leg.br" + href
                        elif not href.startswith("http"):
                            href = "https://www.al.to.leg.br/" + href
                        pdf_links.append(href)
                
                # Busca por botões ou links que podem levar ao PDF
                for element in bloco.find_all(["a", "button"], text=re.compile(r"(PDF|pdf|Baixar|Download|Ver Lei)", re.I)):
                    href = element.get("href", "")
                    onclick = element.get("onclick", "")
                    
                    if href and not href.startswith("#"):
                        if href.startswith("/"):
                            href = "https://www.al.to.leg.br" + href
                        elif not href.startswith("http"):
                            href = "https://www.al.to.leg.br/" + href
                        pdf_links.append(href)
                    
                    # Extrai URLs de onclick
                    if onclick:
                        url_match = re.search(r"['\"]([^'\"]*\.pdf[^'\"]*)['\"]", onclick)
                        if url_match:
                            url = url_match.group(1)
                            if url.startswith("/"):
                                url = "https://www.al.to.leg.br" + url
                            pdf_links.append(url)
                
                if pdf_links:
                    leis_com_pdf.append({
                        "titulo": titulo,
                        "descricao": descricao,
                        "conteudo_preview": conteudo_preview,
                        "pdf_links": list(set(pdf_links))  # Remove duplicatas
                    })
                    
            except Exception as e:
                print(f"Erro ao processar bloco: {e}")
                continue
        
        return leis_com_pdf
    
    def download_pdf_content(self, pdf_url: str) -> Optional[str]:
        """Baixa e extrai texto de um PDF"""
        try:
            print(f"Baixando PDF: {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Verifica se é realmente um PDF
            if 'application/pdf' not in response.headers.get('content-type', ''):
                print(f"URL não é um PDF válido: {pdf_url}")
                return None
            
            # Extrai texto do PDF
            pdf_file = io.BytesIO(response.content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            texto_completo = ""
            for page in pdf_reader.pages:
                texto_completo += page.extract_text() + "\n"
            
            return texto_completo.strip()
            
        except Exception as e:
            print(f"Erro ao baixar/processar PDF {pdf_url}: {e}")
            return None
    
    def collect_all_pdf_laws(self, max_pages: int = 250) -> List[Dict]:
        """Coleta todas as leis ambientais com conteúdo completo dos PDFs"""
        driver = self.setup_driver()
        leis_completas = []
        
        try:
            for pagina in range(1, max_pages + 1):
                print(f"Processando página {pagina}/{max_pages}")
                
                url = f"{self.base_url}?pagPaginaAtual={pagina}"
                driver.get(url)
                time.sleep(3)  # Aguarda carregamento
                
                html_content = driver.page_source
                leis_com_pdf = self.extract_pdf_links_from_page(html_content)
                
                for lei in leis_com_pdf:
                    print(f"Processando lei: {lei['titulo'][:50]}...")
                    
                    # Tenta baixar o conteúdo de cada PDF
                    conteudo_completo = lei['conteudo_preview']
                    
                    for pdf_url in lei['pdf_links']:
                        pdf_content = self.download_pdf_content(pdf_url)
                        if pdf_content:
                            conteudo_completo = pdf_content
                            break  # Usa o primeiro PDF que conseguir baixar
                    
                    lei_completa = {
                        "titulo": lei['titulo'],
                        "descricao": lei['descricao'],
                        "conteudo": conteudo_completo,
                        "fonte": "PDF" if conteudo_completo != lei['conteudo_preview'] else "HTML",
                        "pdf_links": lei['pdf_links']
                    }
                    
                    leis_completas.append(lei_completa)
                
                # Pequena pausa entre páginas
                time.sleep(2)
                
        finally:
            driver.quit()
        
        return leis_completas

def coletar_leis_pdf():
    """Função principal para coletar leis com PDFs"""
    collector = PDFLeiCollector()
    return collector.collect_all_pdf_laws()

if __name__ == "__main__":
    # Teste do serviço
    leis = coletar_leis_pdf()
    print(f"Total de leis ambientais coletadas: {len(leis)}")
    
    # Salva resultado para análise
    import json
    with open("tests/leis_pdf_completas.json", "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)