#!/usr/bin/env python3
"""
EXEMPLO PRÁTICO: Como modificar ia_tabela_service.py 
para usar APIs do Governo Federal

Este exemplo mostra EXATAMENTE como você integraria as APIs
para substituir os textos pré-definidos por dados reais.
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class IATabela_ComAPIGov:
    """Versão modificada com integração de APIs governamentais"""
    
    def __init__(self):
        # Configurações das APIs
        self.api_dados_abertos = "https://dados.gov.br/api/publico"
        self.api_planalto = "https://www.planalto.gov.br/ccivil_03"
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Cache para evitar múltiplas chamadas
        self._cache_leis = {}
    
    def _legislacoes_federais(self, grupo_atividade: str, limite: int = 10) -> List[Dict]:
        """
        NOVA VERSÃO: Busca descrições REAIS das APIs do governo
        
        FLUXO:
        1. Tenta buscar dados reais das APIs governamentais
        2. Se falhar, usa dados pré-definidos como fallback
        """
        
        print(f"🔍 Buscando legislações federais para {grupo_atividade}...")
        
        # 1️⃣ TENTAR BUSCAR DADOS REAIS DAS APIs
        try:
            legislacoes_api = self._buscar_leis_apis_governo(grupo_atividade, limite)
            
            if legislacoes_api and len(legislacoes_api) > 0:
                print(f"✅ Encontradas {len(legislacoes_api)} leis nas APIs governamentais")
                return legislacoes_api
            else:
                print("⚠️ Nenhuma lei encontrada nas APIs")
        
        except Exception as e:
            print(f"❌ Erro ao acessar APIs: {e}")
        
        # 2️⃣ FALLBACK: Usar dados pré-definidos
        print("🔄 Usando dados de fallback...")
        return self._legislacoes_federais_fallback(grupo_atividade, limite)
    
    def _buscar_leis_apis_governo(self, grupo_atividade: str, limite: int) -> List[Dict]:
        """Busca leis federais nas APIs do governo"""
        
        legislacoes_encontradas = []
        
        # Lista de leis federais importantes por atividade
        leis_por_atividade = {
            "Agricultura": [
                {"numero": "12651", "ano": "2012", "nome": "Código Florestal"},
                {"numero": "6938", "ano": "1981", "nome": "Política Nacional do Meio Ambiente"},
                {"numero": "12305", "ano": "2010", "nome": "Política Nacional de Resíduos Sólidos"}
            ],
            "Pecuária": [
                {"numero": "12651", "ano": "2012", "nome": "Código Florestal"},
                {"numero": "9013", "ano": "2017", "nome": "Regulamento de Inspeção Industrial"},
                {"numero": "9605", "ano": "1998", "nome": "Lei de Crimes Ambientais"}
            ],
            "Indústria": [
                {"numero": "6938", "ano": "1981", "nome": "Política Nacional do Meio Ambiente"},
                {"numero": "12305", "ano": "2010", "nome": "Política Nacional de Resíduos Sólidos"},
                {"numero": "9605", "ano": "1998", "nome": "Lei de Crimes Ambientais"}
            ],
            "Mineração": [
                {"numero": "227", "ano": "1967", "nome": "Código de Mineração"},
                {"numero": "13540", "ano": "2017", "nome": "Compensação Financeira Mineração"},
                {"numero": "6938", "ano": "1981", "nome": "Política Nacional do Meio Ambiente"}
            ]
        }
        
        leis_relevantes = leis_por_atividade.get(grupo_atividade, [])
        
        # Buscar cada lei nas APIs
        for lei_info in leis_relevantes[:limite]:
            try:
                dados_lei = self._buscar_lei_especifica(lei_info["numero"], lei_info["ano"])
                
                if dados_lei:
                    # Converter para formato esperado pela tabela
                    lei_formatada = self._formatar_lei_para_tabela(dados_lei, grupo_atividade)
                    legislacoes_encontradas.append(lei_formatada)
                    
                    print(f"✅ Lei {lei_info['numero']}/{lei_info['ano']} encontrada")
                else:
                    print(f"⚠️ Lei {lei_info['numero']}/{lei_info['ano']} não encontrada")
            
            except Exception as e:
                print(f"❌ Erro ao buscar lei {lei_info['numero']}: {e}")
        
        return legislacoes_encontradas
    
    def _buscar_lei_especifica(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca uma lei específica nas APIs do governo"""
        
        # Verificar cache primeiro
        cache_key = f"{numero_lei}_{ano}"
        if cache_key in self._cache_leis:
            return self._cache_leis[cache_key]
        
        # MÉTODO 1: Portal de Dados Abertos
        dados_portal = self._buscar_portal_dados_abertos(numero_lei, ano)
        if dados_portal:
            self._cache_leis[cache_key] = dados_portal
            return dados_portal
        
        # MÉTODO 2: Scraping estruturado do Planalto
        dados_planalto = self._buscar_planalto_estruturado(numero_lei, ano)
        if dados_planalto:
            self._cache_leis[cache_key] = dados_planalto
            return dados_planalto
        
        # MÉTODO 3: Base dos Dados (se disponível)
        dados_base = self._buscar_base_dados(numero_lei, ano)
        if dados_base:
            self._cache_leis[cache_key] = dados_base
            return dados_base
        
        return None
    
    def _buscar_portal_dados_abertos(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca no Portal de Dados Abertos"""
        
        try:
            params = {
                'q': f"lei {numero_lei} {ano}",
                'rows': 5,
                'fq': 'organization:ministerio-do-meio-ambiente'
            }
            
            response = self.session.get(
                f"{self.api_dados_abertos}/conjuntos-dados",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for dataset in data.get('result', []):
                    if self._validar_dataset_lei(dataset, numero_lei, ano):
                        return self._extrair_dados_dataset(dataset, numero_lei, ano)
        
        except Exception as e:
            print(f"Erro Portal Dados Abertos: {e}")
        
        return None
    
    def _buscar_planalto_estruturado(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca estruturada no site do Planalto"""
        
        try:
            # URLs possíveis no Planalto
            urls_possiveis = [
                f"{self.api_planalto}/leis/l{numero_lei}.htm",
                f"{self.api_planalto}/leis/L{numero_lei}.htm",
                f"{self.api_planalto}/decreto-lei/del{numero_lei}.htm"
            ]
            
            for url in urls_possiveis:
                try:
                    response = self.session.get(url)
                    
                    if response.status_code == 200:
                        return self._extrair_dados_planalto(response.text, numero_lei, ano, url)
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"Erro Planalto: {e}")
        
        return None
    
    def _buscar_base_dados(self, numero_lei: str, ano: str) -> Optional[Dict]:
        """Busca na Base dos Dados (se disponível)"""
        
        # Implementar se a Base dos Dados tiver API disponível
        return None
    
    def _validar_dataset_lei(self, dataset: Dict, numero_lei: str, ano: str) -> bool:
        """Valida se o dataset corresponde à lei procurada"""
        
        title = dataset.get('title', '').lower()
        notes = dataset.get('notes', '').lower()
        
        return (
            numero_lei in title or numero_lei in notes
        ) and (
            ano in title or ano in notes
        )
    
    def _extrair_dados_dataset(self, dataset: Dict, numero_lei: str, ano: str) -> Dict:
        """Extrai dados do dataset do Portal de Dados Abertos"""
        
        return {
            'numero': numero_lei,
            'ano': ano,
            'titulo': dataset.get('title', f'Lei nº {numero_lei}/{ano}'),
            'descricao_resumida': self._limpar_descricao(dataset.get('notes', '')),
            'ementa': dataset.get('notes', ''),
            'fonte': 'Portal de Dados Abertos',
            'url': dataset.get('url', ''),
            'organizacao': dataset.get('organization', {}).get('title', ''),
            'status': 'vigente',
            'data_atualizacao': datetime.now().isoformat()
        }
    
    def _extrair_dados_planalto(self, html: str, numero_lei: str, ano: str, url: str) -> Dict:
        """Extrai dados do HTML do Planalto"""
        
        # Implementar parsing HTML básico
        # Por simplicidade, retornando estrutura básica
        
        return {
            'numero': numero_lei,
            'ano': ano,
            'titulo': f'Lei nº {numero_lei}, de {ano}',
            'descricao_resumida': self._extrair_ementa_html(html),
            'ementa': self._extrair_ementa_html(html),
            'fonte': 'Planalto',
            'url': url,
            'status': 'vigente',
            'data_atualizacao': datetime.now().isoformat()
        }
    
    def _extrair_ementa_html(self, html: str) -> str:
        """Extrai ementa do HTML (implementação simplificada)"""
        
        # Buscar padrões comuns de ementa
        import re
        
        patterns = [
            r'Dispõe sobre[^.]+\.',
            r'Institui[^.]+\.',
            r'Estabelece[^.]+\.',
            r'Regulamenta[^.]+\.'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Ementa não encontrada no documento oficial"
    
    def _formatar_lei_para_tabela(self, dados_lei: Dict, grupo_atividade: str) -> Dict:
        """Formata dados da API para o formato esperado pela tabela"""
        
        return {
            "esfera": "Federal",
            "titulo_legislacao": dados_lei.get('titulo', f"Lei nº {dados_lei.get('numero')}/{dados_lei.get('ano')}"),
            "vigencia": "✅ Vigente",
            "descricao_resumida": self._limitar_descricao(dados_lei.get('descricao_resumida', '')),
            "aplicabilidade": self._gerar_aplicabilidade(dados_lei, grupo_atividade),
            "fonte_dados": dados_lei.get('fonte', 'API Governo'),
            "url_oficial": dados_lei.get('url', ''),
            "data_atualizacao": dados_lei.get('data_atualizacao', '')
        }
    
    def _limpar_descricao(self, descricao: str) -> str:
        """Limpa e formata a descrição"""
        
        if not descricao:
            return "Descrição não disponível"
        
        # Remover HTML tags se houver
        import re
        descricao = re.sub(r'<[^>]+>', '', descricao)
        
        # Limitar tamanho
        return descricao[:200] + "..." if len(descricao) > 200 else descricao
    
    def _limitar_descricao(self, descricao: str) -> str:
        """Limita tamanho da descrição"""
        
        if not descricao:
            return "Descrição não disponível"
        
        return descricao[:150] + "..." if len(descricao) > 150 else descricao
    
    def _gerar_aplicabilidade(self, dados_lei: Dict, grupo_atividade: str) -> str:
        """Gera texto de aplicabilidade baseado na lei e atividade"""
        
        aplicabilidades = {
            "6938": f"Licenciamento ambiental obrigatório para atividades de {grupo_atividade.lower()} potencialmente poluidoras",
            "12651": f"Obrigatória para propriedades rurais - Reserva Legal mínima de 35% no Cerrado do Tocantins",
            "9605": f"Define crimes ambientais aplicáveis a {grupo_atividade.lower()}, como poluição e desmatamento ilegal",
            "12305": f"Gestão obrigatória de resíduos sólidos em atividades de {grupo_atividade.lower()}"
        }
        
        numero_lei = dados_lei.get('numero', '')
        return aplicabilidades.get(numero_lei, f"Aplicável a atividades de {grupo_atividade.lower()}")
    
    def _legislacoes_federais_fallback(self, grupo_atividade: str, limite: int) -> List[Dict]:
        """Dados de fallback (versão original) caso APIs falhem"""
        
        # Esta seria a função original com dados pré-definidos
        # Mantida apenas como backup
        
        legislacoes_fallback = {
            "Agricultura": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.651, de 25 de maio de 2012 (Código Florestal Brasileiro)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dispõe sobre a proteção da vegetação nativa, define Áreas de Preservação Permanente e Reserva Legal",
                    "aplicabilidade": "Obrigatória para propriedades rurais - Reserva Legal mínima de 35% no Cerrado do Tocantins"
                }
                # ... outros dados pré-definidos
            ]
            # ... outras atividades
        }
        
        return legislacoes_fallback.get(grupo_atividade, [])[:limite]

# EXEMPLO DE USO
def exemplo_uso():
    """Exemplo de como a nova versão funcionaria"""
    
    print("🚀 EXEMPLO: Nova versão com APIs do Governo")
    print("=" * 50)
    
    tabela = IATabela_ComAPIGov()
    
    # Buscar legislações para agricultura
    legislacoes = tabela._legislacoes_federais("Agricultura", limite=3)
    
    print(f"\n📋 Encontradas {len(legislacoes)} legislações:")
    
    for i, lei in enumerate(legislacoes, 1):
        print(f"\n{i}. {lei['titulo_legislacao']}")
        print(f"   📝 Descrição: {lei['descricao_resumida']}")
        print(f"   🎯 Aplicabilidade: {lei['aplicabilidade']}")
        print(f"   🏛️ Fonte: {lei.get('fonte_dados', 'Dados pré-definidos')}")

if __name__ == "__main__":
    exemplo_uso()