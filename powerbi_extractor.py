#!/usr/bin/env python3
"""
Extrator de dados para Dashboard Power BI
Versão híbrida: requests + Selenium (quando disponível)
"""

import time
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from multi_source_indexer import MultiSourceIndexer

class PowerBIExtractor:
    """Extrator de dados para dashboards Power BI"""
    
    def __init__(self, dashboard_url: str):
        self.dashboard_url = dashboard_url
        self.session = requests.Session()
        
        # Headers para parecer um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_with_requests(self) -> dict:
        """Extrai dados usando requests (método básico)"""
        print(f"🔍 Tentando extração básica com requests...")
        
        try:
            response = self.session.get(self.dashboard_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrai texto visível
            text = soup.get_text(separator=' ', strip=True)
            
            # Procura por dados específicos
            data_elements = self._extract_basic_data(soup, response.text)
            
            return {
                'source': 'Power BI Dashboard (Basic)',
                'url': self.dashboard_url,
                'text': text,
                'type': 'dashboard',
                'collected_at': datetime.now().isoformat(),
                'data_elements': data_elements,
                'page_title': soup.title.string if soup.title else 'N/A',
                'method': 'requests',
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            
        except Exception as e:
            print(f"❌ Erro na extração básica: {e}")
            return None
    
    def _extract_basic_data(self, soup: BeautifulSoup, raw_html: str) -> dict:
        """Extrai dados básicos do HTML"""
        data = {
            'titles': [],
            'scripts': [],
            'meta_info': [],
            'embedded_data': []
        }
        
        # Procura por títulos
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            titles = soup.find_all(tag)
            for title in titles:
                text = title.get_text(strip=True)
                if text and len(text) > 2:
                    data['titles'].append(text)
        
        # Procura por meta informações
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') or meta.get('property'):
                data['meta_info'].append({
                    'name': meta.get('name') or meta.get('property'),
                    'content': meta.get('content', '')
                })
        
        # Procura por dados embarcados em scripts
        import re
        
        # Procura por configurações do Power BI
        powerbi_patterns = [
            r'powerbi[^"]*',
            r'dashboard[^"]*',
            r'report[^"]*',
            r'visual[^"]*'
        ]
        
        for pattern in powerbi_patterns:
            matches = re.findall(pattern, raw_html, re.IGNORECASE)
            data['embedded_data'].extend(matches[:10])  # Primeiros 10 matches
        
        # Procura por URLs de API
        api_patterns = [
            r'https://[^"]*api[^"]*',
            r'https://[^"]*powerbi[^"]*'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, raw_html)
            data['embedded_data'].extend(matches[:5])  # Primeiros 5 matches
        
        return data
    
    def extract_with_selenium(self) -> dict:
        """Extrai dados usando Selenium (método avançado)"""
        print(f"🔍 Tentando extração avançada com Selenium...")
        
        try:
            # Tenta importar Selenium
            from selenium import webdriver
            from selenium.webdriver.edge.service import Service as EdgeService
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Configura opções do Edge
            options = webdriver.EdgeOptions()
            options.add_argument('--headless')  # Executa em background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Tenta usar driver local se existir
            driver_path = "msedgedriver.exe"
            try:
                service = EdgeService(executable_path=driver_path)
                driver = webdriver.Edge(service=service, options=options)
            except:
                print("❌ Driver local não encontrado, tentando webdriver-manager...")
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            
            try:
                # Acessa o dashboard
                driver.get(self.dashboard_url)
                
                # Aguarda carregamento
                time.sleep(15)
                
                # Extrai conteúdo
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Remove scripts e estilos
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text(separator=' ', strip=True)
                data_elements = self._extract_advanced_data(soup, driver)
                
                # Tira screenshot
                screenshot_path = f"powerbi_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                
                return {
                    'source': 'Power BI Dashboard (Advanced)',
                    'url': self.dashboard_url,
                    'text': text,
                    'type': 'dashboard',
                    'collected_at': datetime.now().isoformat(),
                    'data_elements': data_elements,
                    'page_title': driver.title,
                    'method': 'selenium',
                    'screenshot': screenshot_path
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Erro na extração avançada: {e}")
            return None
    
    def _extract_advanced_data(self, soup: BeautifulSoup, driver) -> dict:
        """Extrai dados avançados usando Selenium"""
        data = {
            'titles': [],
            'interactive_elements': [],
            'visual_containers': [],
            'data_values': []
        }
        
        try:
            # Procura por elementos interativos
            interactive_selectors = [
                "[data-testid]",
                "[role='button']",
                "[role='tab']",
                ".visual-container",
                ".powerbi-visual"
            ]
            
            for selector in interactive_selectors:
                try:
                    elements = driver.find_elements("css selector", selector)
                    for elem in elements[:10]:  # Primeiros 10
                        text = elem.text.strip()
                        if text and len(text) > 1:
                            data['interactive_elements'].append(text)
                except:
                    continue
            
            # Procura por títulos
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                titles = soup.find_all(tag)
                for title in titles:
                    text = title.get_text(strip=True)
                    if text and len(text) > 2:
                        data['titles'].append(text)
            
        except Exception as e:
            print(f"⚠️  Erro ao extrair dados avançados: {e}")
        
        return data
    
    def extract_data(self) -> dict:
        """Método principal de extração"""
        print(f"🚀 INICIANDO EXTRAÇÃO DO DASHBOARD POWER BI")
        print(f"URL: {self.dashboard_url}")
        print("=" * 60)
        
        # Tenta primeiro com requests
        data = self.extract_with_requests()
        
        if data and len(data['text']) > 100:
            print(f"✅ Extração básica bem-sucedida!")
            return data
        
        # Se requests não funcionou bem, tenta Selenium
        print(f"🔄 Tentando método avançado...")
        selenium_data = self.extract_with_selenium()
        
        if selenium_data:
            print(f"✅ Extração avançada bem-sucedida!")
            return selenium_data
        
        # Se nenhum método funcionou, retorna o que conseguiu
        if data:
            print(f"⚠️  Retornando dados básicos disponíveis")
            return data
        
        print(f"❌ Falha em todos os métodos de extração")
        return None
    
    def save_to_file(self, data: dict, filename: str = None):
        """Salva os dados extraídos em arquivo"""
        if not filename:
            filename = f"powerbi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Dados salvos em: {filename}")
        return filename

def main():
    """Função principal"""
    # URL do dashboard fornecida pelo usuário
    dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiZGEyMzBkMWYtNzNiMS00ZmIyLTg5YzgtZDk5ZWE5ODU4ZDg2IiwidCI6IjJiMjY2ZmE5LTNmOTMtNGJiMS05ODMwLTYzNDY3NTJmMDNlNCIsImMiOjF9"
    
    # Cria o extrator
    extractor = PowerBIExtractor(dashboard_url)
    
    # Extrai os dados
    data = extractor.extract_data()
    
    if data:
        print(f"\n📊 DADOS EXTRAÍDOS:")
        print(f"   Método: {data.get('method', 'N/A')}")
        print(f"   Título da página: {data.get('page_title', 'N/A')}")
        print(f"   Tamanho do texto: {len(data['text']):,} caracteres")
        print(f"   Elementos encontrados: {len(data['data_elements'])}")
        
        if 'status_code' in data:
            print(f"   Status HTTP: {data['status_code']}")
        if 'content_length' in data:
            print(f"   Tamanho do conteúdo: {data['content_length']:,} bytes")
        
        # Salva os dados
        filename = extractor.save_to_file(data)
        
        # Tenta indexar no sistema
        print(f"\n🔄 INDEXANDO NO SISTEMA...")
        try:
            indexer = MultiSourceIndexer()
            
            # Prepara o documento para indexação
            custom_docs = [{
                'text': data['text'],
                'url': data['url'],
                'type': data['type']
            }]
            
            indexer.add_custom_source("Power BI Dashboard", custom_docs)
            print(f"✅ Dashboard indexado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao indexar: {e}")
            print(f"💡 Dados salvos em {filename} para indexação manual")
        
        print(f"\n🎉 EXTRAÇÃO CONCLUÍDA!")
        print(f"📁 Arquivo de dados: {filename}")
        
        # Mostra preview dos dados
        print(f"\n📋 PREVIEW DOS DADOS:")
        print(f"   Primeiros 200 caracteres do texto:")
        print(f"   {data['text'][:200]}...")
        
    else:
        print(f"❌ Falha na extração dos dados")

if __name__ == "__main__":
    main()