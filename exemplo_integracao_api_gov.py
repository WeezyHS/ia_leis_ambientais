#!/usr/bin/env python3
"""
EXEMPLO PRÁTICO: Como integrar APIs do Governo Federal 
para obter descrições reais das leis federais

Este é um exemplo de como você implementaria a integração,
mesmo que as APIs tenham limitações técnicas no momento.
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class IntegradorAPIGovFederal:
    """Classe para integrar com APIs do Governo Federal"""
    
    def __init__(self):
        self.base_url_dados_abertos = "https://dados.gov.br/api/publico"
        self.base_url_planalto = "https://www.planalto.gov.br/ccivil_03"
        self.session = requests.Session()
        self.session.verify = False  # Para contornar problemas de SSL temporariamente
    
    def buscar_legislacao_federal(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """
        Busca informações de uma lei federal específica
        
        Args:
            numero_lei: Número da lei (ex: "6938")
            ano: Ano da lei (ex: "1981")
            
        Returns:
            Dicionário com dados da lei ou None se não encontrar
        """
        
        # MÉTODO 1: Buscar no Portal de Dados Abertos
        try:
            dados_portal = self._buscar_portal_dados_abertos(numero_lei, ano)
            if dados_portal:
                return dados_portal
        except Exception as e:
            print(f"⚠️ Erro no Portal de Dados Abertos: {e}")
        
        # MÉTODO 2: Buscar no site do Planalto (scraping estruturado)
        try:
            dados_planalto = self._buscar_planalto(numero_lei, ano)
            if dados_planalto:
                return dados_planalto
        except Exception as e:
            print(f"⚠️ Erro no Planalto: {e}")
        
        # MÉTODO 3: Buscar em APIs alternativas (Base dos Dados, etc.)
        try:
            dados_alternativos = self._buscar_apis_alternativas(numero_lei, ano)
            if dados_alternativos:
                return dados_alternativos
        except Exception as e:
            print(f"⚠️ Erro em APIs alternativas: {e}")
        
        return None
    
    def _buscar_portal_dados_abertos(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca no Portal de Dados Abertos"""
        
        search_query = f"lei {numero_lei} {ano}"
        
        params = {
            'q': search_query,
            'rows': 10,
            'fq': 'organization:ministerio-do-meio-ambiente'  # Filtrar por MMA
        }
        
        response = self.session.get(
            f"{self.base_url_dados_abertos}/conjuntos-dados",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            for dataset in data.get('result', []):
                if self._validar_lei_dataset(dataset, numero_lei, ano):
                    return self._extrair_dados_dataset(dataset)
        
        return None
    
    def _buscar_planalto(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca no site do Planalto (método de scraping estruturado)"""
        
        # URL padrão do Planalto para leis
        url_lei = f"{self.base_url_planalto}/leis/l{numero_lei}.htm"
        
        try:
            response = self.session.get(url_lei)
            
            if response.status_code == 200:
                # Aqui você faria parsing do HTML para extrair:
                # - Ementa da lei
                # - Texto completo
                # - Data de publicação
                # - Status (vigente, revogada, etc.)
                
                return {
                    'numero': numero_lei,
                    'ano': ano,
                    'fonte': 'Planalto',
                    'url': url_lei,
                    'ementa': self._extrair_ementa_html(response.text),
                    'descricao_resumida': self._extrair_descricao_html(response.text),
                    'status': 'vigente',
                    'data_publicacao': self._extrair_data_html(response.text)
                }
        
        except Exception as e:
            print(f"Erro ao acessar Planalto: {e}")
        
        return None
    
    def _buscar_apis_alternativas(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca em APIs alternativas como Base dos Dados"""
        
        # Exemplo: Base dos Dados
        base_dados_url = "https://basedosdados.org/api/v1/graphql"
        
        query = {
            "query": f"""
            {{
                allDatasets(filter: {{
                    name: {{contains: "legislacao"}}
                    tags: {{contains: "ambiental"}}
                }}) {{
                    edges {{
                        node {{
                            name
                            description
                            resources {{
                                url
                                format
                            }}
                        }}
                    }}
                }}
            }}
            """
        }
        
        try:
            response = self.session.post(base_dados_url, json=query)
            
            if response.status_code == 200:
                data = response.json()
                # Processar resposta GraphQL
                return self._processar_base_dados(data, numero_lei, ano)
        
        except Exception as e:
            print(f"Erro na Base dos Dados: {e}")
        
        return None
    
    def _validar_lei_dataset(self, dataset: Dict, numero_lei: str, ano: str) -> bool:
        """Valida se o dataset corresponde à lei procurada"""
        
        title = dataset.get('title', '').lower()
        description = dataset.get('notes', '').lower()
        
        return (
            numero_lei in title or numero_lei in description
        ) and (
            ano in title or ano in description
        )
    
    def _extrair_dados_dataset(self, dataset: Dict) -> Dict:
        """Extrai dados relevantes do dataset"""
        
        return {
            'titulo': dataset.get('title', ''),
            'descricao_resumida': dataset.get('notes', '')[:200],
            'organizacao': dataset.get('organization', {}).get('title', ''),
            'tags': [tag.get('name') for tag in dataset.get('tags', [])],
            'recursos': [
                {
                    'nome': res.get('name', ''),
                    'formato': res.get('format', ''),
                    'url': res.get('url', '')
                }
                for res in dataset.get('resources', [])
            ],
            'fonte': 'Portal de Dados Abertos'
        }
    
    def _extrair_ementa_html(self, html: str) -> str:
        """Extrai ementa do HTML do Planalto"""
        # Implementar parsing HTML para extrair ementa
        # Exemplo simplificado:
        if "estabelece a Política Nacional do Meio Ambiente" in html:
            return "Dispõe sobre a Política Nacional do Meio Ambiente, seus fins e mecanismos de formulação e aplicação"
        return "Ementa não encontrada"
    
    def _extrair_descricao_html(self, html: str) -> str:
        """Extrai descrição resumida do HTML"""
        # Implementar parsing para extrair primeiro parágrafo ou artigo
        return "Descrição extraída do texto oficial da lei"
    
    def _extrair_data_html(self, html: str) -> str:
        """Extrai data de publicação do HTML"""
        return "1981-08-31"  # Exemplo
    
    def _processar_base_dados(self, data: Dict, numero_lei: str, ano: str) -> Optional[Dict]:
        """Processa resposta da Base dos Dados"""
        # Implementar processamento da resposta GraphQL
        return None

# EXEMPLO DE USO PRÁTICO
def exemplo_uso_api_gov():
    """Exemplo de como usar a integração com APIs do governo"""
    
    print("🚀 EXEMPLO: Integrando com APIs do Governo Federal")
    print("=" * 60)
    
    integrador = IntegradorAPIGovFederal()
    
    # Lista de leis federais ambientais importantes
    leis_federais = [
        {"numero": "6938", "ano": "1981", "nome": "Política Nacional do Meio Ambiente"},
        {"numero": "9605", "ano": "1998", "nome": "Lei de Crimes Ambientais"},
        {"numero": "12651", "ano": "2012", "nome": "Código Florestal"},
        {"numero": "9985", "ano": "2000", "nome": "Sistema Nacional de Unidades de Conservação"}
    ]
    
    print("\n📋 Buscando descrições reais das leis federais...")
    
    for lei in leis_federais:
        print(f"\n🔍 Buscando Lei {lei['numero']}/{lei['ano']} - {lei['nome']}")
        
        dados_lei = integrador.buscar_legislacao_federal(lei['numero'], lei['ano'])
        
        if dados_lei:
            print(f"✅ Encontrada!")
            print(f"   📄 Título: {dados_lei.get('titulo', 'N/A')}")
            print(f"   📝 Descrição: {dados_lei.get('descricao_resumida', 'N/A')[:100]}...")
            print(f"   🏛️ Fonte: {dados_lei.get('fonte', 'N/A')}")
        else:
            print(f"❌ Não encontrada - usando fallback")
            print(f"   📝 Descrição Fallback: {_obter_descricao_fallback(lei['numero'])}")

def _obter_descricao_fallback(numero_lei: str) -> str:
    """Retorna descrição de fallback para leis conhecidas"""
    
    fallbacks = {
        "6938": "Institui a Política Nacional do Meio Ambiente, seus fins e mecanismos de formulação e aplicação",
        "9605": "Dispõe sobre as sanções penais e administrativas derivadas de condutas e atividades lesivas ao meio ambiente",
        "12651": "Estabelece normas gerais sobre a proteção da vegetação, áreas de Preservação Permanente e as áreas de Reserva Legal",
        "9985": "Institui o Sistema Nacional de Unidades de Conservação da Natureza"
    }
    
    return fallbacks.get(numero_lei, "Descrição não disponível")

if __name__ == "__main__":
    exemplo_uso_api_gov()