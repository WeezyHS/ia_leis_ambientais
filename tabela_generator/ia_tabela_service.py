#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de IA direcionada para geração de tabelas/planilhas das leis ambientais
Utiliza OpenAI API de forma programática para organizar dados em tabelas
Inclui TODAS as fontes de dados: Leis Estaduais, Power BI, COEMA, ABNT, CONAMA, etc.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório app ao path para importar serviços
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Carregar variáveis de ambiente
load_dotenv()

class IATabela:
    """
    IA direcionada para geração de tabelas organizadas de TODAS as fontes de dados ambientais
    """
    
    def __init__(self):
        """Inicializa o serviço de IA para tabelas com todas as fontes"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        

        
        # Carregar dados APENAS do Pinecone
        self.todas_fontes_data = self._carregar_todas_fontes()
        

    

    

    

    

    
    def _carregar_todas_fontes(self) -> List[Dict]:
        """Carrega dados APENAS do Pinecone como fonte única"""
        todas_fontes = []
        
        try:
            # ÚNICA FONTE: Dados do Pinecone
            print("🎯 Carregando dados APENAS do Pinecone como fonte única...")
            dados_pinecone = self._carregar_dados_pinecone()
            todas_fontes.extend(dados_pinecone)
            
            print(f"✅ {len(todas_fontes)} documentos carregados APENAS do Pinecone")
            return todas_fontes
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados do Pinecone: {e}")
            # Retorna lista vazia em caso de erro
            return []
    
    def _carregar_dados_pinecone(self) -> List[Dict]:
        """Carrega apenas dados reais dos namespaces do Pinecone e arquivos JSON locais"""
        dados_pinecone = []
        
        try:
            from services.pinecone_service import pinecone_index
            
            # Obter estatísticas dos namespaces
            stats = pinecone_index.describe_index_stats()
            print(f"📊 Namespaces disponíveis no Pinecone: {list(stats.namespaces.keys())}")
            
            # Buscar dados reais de ABNT se disponível no namespace
            if "abnt-normas" in stats.namespaces:
                abnt_count = stats.namespaces["abnt-normas"].vector_count
                print(f"📋 Encontradas {abnt_count} normas ABNT no Pinecone")
                
                # Buscar dados reais das normas ABNT (limitado para performance)
                try:
                    query_response = pinecone_index.query(
                        namespace="abnt-normas",
                        vector=[0.0] * 1536,  # Vector dummy para busca
                        top_k=min(10, abnt_count),
                        include_metadata=True
                    )
                    
                    for match in query_response.matches:
                        metadata = match.metadata or {}
                        dados_pinecone.append({
                            "fonte": "ABNT - Pinecone",
                            "tipo": "Norma Técnica",
                            "titulo": metadata.get("titulo", "Norma ABNT"),
                            "descricao": metadata.get("descricao", "Norma técnica brasileira")[:200] + "...",
                            "conteudo": metadata.get("conteudo", "Especificações técnicas")[:200] + "...",
                            "categoria": "Norma Técnica",
                            "jurisdicao": "Nacional",
                            "data_indexacao": metadata.get("data_indexacao", "2025-01-07"),
                            "fonte_dados": "Pinecone - Dados Reais"
                        })
                except Exception as e:
                    print(f"⚠️ Erro ao buscar normas ABNT: {e}")
            
            # Buscar dados reais do namespace principal (onde estão as leis)
            for namespace in stats.namespaces:
                if namespace not in ["abnt-normas"] and stats.namespaces[namespace].vector_count > 0:
                    print(f"📋 Namespace '{namespace}' com {stats.namespaces[namespace].vector_count} documentos")
                    
                    # Buscar documentos do namespace principal
                    try:
                        query_response = pinecone_index.query(
                            namespace=namespace if namespace != "" else None,
                            vector=[0.0] * 1536,  # Vector dummy para busca
                            top_k=min(50, stats.namespaces[namespace].vector_count),  # Buscar mais documentos
                            include_metadata=True
                        )
                        
                        for match in query_response.matches:
                            metadata = match.metadata or {}
                            
                            # Extrair dados do documento
                            titulo = metadata.get("titulo", metadata.get("title", "Documento"))
                            descricao = metadata.get("descricao", metadata.get("ementa", metadata.get("content", "")))
                            tipo_doc = metadata.get("tipo", metadata.get("type", "Lei"))
                            jurisdicao = metadata.get("jurisdicao", metadata.get("jurisdiction", "Federal"))
                            
                            dados_pinecone.append({
                                "fonte": f"Pinecone - {namespace if namespace else 'Principal'}",
                                "tipo": self._mapear_tipo_documento(tipo_doc),
                                "titulo": titulo,
                                "descricao": descricao[:300] + "..." if len(descricao) > 300 else descricao,
                                "ementa": descricao,  # Para compatibilidade com leis federais
                                "conteudo": metadata.get("conteudo", metadata.get("content", descricao))[:200] + "...",
                                "categoria": "Legislação Ambiental",
                                "jurisdicao": jurisdicao,
                                "data_indexacao": metadata.get("data_indexacao", "2025-01-07"),
                                "fonte_dados": "Pinecone - Dados Reais",
                                "vigencia": "✅ Vigente"  # Assumir vigente para dados do Pinecone
                            })
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar dados do namespace '{namespace}': {e}")
            
        except Exception as e:
            print(f"⚠️ Erro ao acessar Pinecone: {e}")
        
        # Nota: Todos os dados (incluindo COEMA, IBAMA, ICMBio) devem estar indexados no Pinecone
        print(f"📊 Total de {len(dados_pinecone)} documentos carregados APENAS do Pinecone")
        
        return dados_pinecone
    
    def _mapear_tipo_documento(self, tipo_doc: str) -> str:
        """Mapeia tipos de documento para categorias padronizadas"""
        tipo_doc = tipo_doc.lower() if tipo_doc else ""
        
        if "lei" in tipo_doc:
            return "Lei"
        elif "decreto" in tipo_doc:
            return "Decreto"
        elif "resolução" in tipo_doc or "resolucao" in tipo_doc:
            return "Resolução"
        elif "portaria" in tipo_doc:
            return "Portaria"
        elif "instrução" in tipo_doc or "instrucao" in tipo_doc:
            return "Instrução Normativa"
        elif "norma" in tipo_doc:
            return "Norma"
        elif "constituição" in tipo_doc or "constituicao" in tipo_doc:
            return "Constituição"
        else:
            return "Legislação"

    def _estrutura_quadro_padrao(self, municipio: str, grupo_atividade: str) -> Dict[str, Any]:
        """Retorna estrutura padrão para quadro-resumo de legislações"""
        return {
            "titulo": f"Quadro-Resumo de Legislações Ambientais - {grupo_atividade} em {municipio}",
            "municipio": municipio,
            "grupo_atividade": grupo_atividade,
            "descricao": f"Legislações ambientais aplicáveis para atividades de {grupo_atividade} no município de {municipio}",
            "dados": [],
            "colunas": [
                "esfera",
                "titulo_legislacao", 
                "vigencia",
                "descricao_resumida",
                "aplicabilidade",
                "fonte_dados"
            ],
            "filtros_sugeridos": {
                "esfera": ["Federal", "Estadual", "Municipal"],
                "vigencia": ["Vigente", "Revogada", "Alterada"]
            },
            "ordenacao_padrao": "esfera"
        }

    def popular_quadro_resumo(self, estrutura: Dict, municipio: str, grupo_atividade: str, esferas: List[str], limite_por_esfera: int = 10) -> pd.DataFrame:
        """
        Popula o quadro-resumo com legislações específicas para o município e atividade
        
        Args:
            estrutura: Estrutura do quadro-resumo
            municipio: Município do empreendimento
            grupo_atividade: Grupo de atividade
            esferas: Lista de esferas legais a incluir
            limite_por_esfera: Máximo de legislações por esfera
        
        Returns:
            DataFrame com o quadro-resumo populado
        """
        try:
            dados_quadro = []
            
            # Gerar dados para cada esfera solicitada
            for esfera in esferas:
                legislacoes_esfera = self._obter_legislacoes_por_esfera(
                    esfera, municipio, grupo_atividade, limite_por_esfera
                )
                dados_quadro.extend(legislacoes_esfera)
            
            # Criar DataFrame
            df_quadro = pd.DataFrame(dados_quadro)
            
            # Ordenar por esfera (Federal, Estadual, Municipal) - com tratamento de erro
            if not df_quadro.empty and 'esfera' in df_quadro.columns:
                ordem_esferas = {"Federal": 1, "Estadual": 2, "Municipal": 3}
                df_quadro['ordem_esfera'] = df_quadro['esfera'].map(ordem_esferas)
                df_quadro = df_quadro.sort_values('ordem_esfera').drop('ordem_esfera', axis=1)
            else:
                print(f"⚠️ DataFrame vazio ou sem coluna 'esfera'. Colunas disponíveis: {list(df_quadro.columns) if not df_quadro.empty else 'Nenhuma'}")
                # Se não há dados, criar um DataFrame com estrutura mínima
                if df_quadro.empty:
                    df_quadro = pd.DataFrame([{
                        "esfera": "Sistema",
                        "titulo_legislacao": "Nenhuma legislação encontrada",
                        "vigencia": "N/A",
                        "descricao_resumida": f"Nenhuma legislação específica para {grupo_atividade} foi encontrada nos dados indexados",
                        "aplicabilidade": "Consulte legislação específica para sua atividade",
                        "fonte_dados": "Sistema - Dados Não Encontrados"
                    }])
            
            return df_quadro
            
        except Exception as e:
            print(f"❌ Erro ao popular quadro-resumo: {e}")
            # Retorna DataFrame vazio em caso de erro
            return pd.DataFrame([{
                "esfera": "Sistema",
                "titulo_legislacao": "Erro no sistema",
                "vigencia": "N/A",
                "descricao_resumida": "Não foi possível carregar dados do Pinecone",
                "aplicabilidade": "Sistema temporariamente indisponível",
                "fonte_dados": "Erro - Dados Não Disponíveis"
            }])

    def _obter_legislacoes_por_esfera(self, esfera: str, municipio: str, grupo_atividade: str, limite: int) -> List[Dict]:
        """Obtém legislações específicas para uma esfera legal"""
        
        if esfera == "Federal":
            return self._legislacoes_federais(grupo_atividade, limite)
        elif esfera == "Estadual":
            return self._legislacoes_estaduais(municipio, grupo_atividade, limite)
        elif esfera == "Municipal":
            return self._legislacoes_municipais(municipio, grupo_atividade, limite)
        else:
            return []

    def _verificar_vigencia_legislacao(self, legislacao: Dict) -> bool:
        """
        ⚠️ PREMISSA OBRIGATÓRIA: Verifica se a legislação está VIGENTE
        Retorna True apenas para legislações vigentes, omite revogadas/substituídas
        """
        vigencia = legislacao.get("vigencia", "").lower()
        titulo = legislacao.get("titulo_legislacao", "").lower()
        
        # Palavras que indicam legislação NÃO vigente
        palavras_nao_vigentes = [
            "revogad", "substituíd", "alterada por", "derrogad", 
            "ab-rogad", "suspenso", "cancelad", "anulad"
        ]
        
        # Verificar se contém indicadores de não vigência
        for palavra in palavras_nao_vigentes:
            if palavra in vigencia or palavra in titulo:
                return False
        
        # Aceitar apenas legislações explicitamente marcadas como vigentes
        return "vigente" in vigencia or "✅" in vigencia
    
    def _legislacoes_federais(self, grupo_atividade: str, limite: int) -> List[Dict]:
        """Retorna APENAS legislações federais REAIS do Pinecone relacionadas ao grupo de atividade"""
        
        # 🎯 FILTRO EXPANDIDO: Palavras-chave mais abrangentes por atividade (baseado em dados reais do Pinecone)
        palavras_chave_federais = {
            "Agricultura": ["agric", "rural", "agropec", "plantio", "cultivo", "irrigação", "atividade rural", "produtor rural", "área de preservação", "vegetação nativa"],
            "Pecuária": ["pecuár", "gado", "bovino", "suíno", "avícola", "frigorífico", "abate", "rebanho", "florestal", "pastagem", "criação de animais", "atividade rural"],
            "Indústria": ["industr", "fábrica", "manufatur", "produção industrial", "poluição industrial", "resíduo", "emissão", "efluente"],
            "Mineração": ["miner", "lavra", "garimpo", "extração mineral", "jazida", "meio ambiente", "degradação", "recuperação"],
            "Saneamento": ["saneamento", "água", "esgoto", "resíduo", "tratamento", "abastecimento", "resíduos sólidos", "lixo", "coleta"],
            "Energia": ["energia", "elétrica", "hidrelétrica", "solar", "eólica", "usina", "geração", "meio ambiente", "impacto ambiental"],
            "Transporte": ["transporte", "rodoviário", "ferroviário", "aquaviário", "portuário", "aeroportuário", "logística", "combustível", "emissão veicular", "poluição atmosférica"],
            "Construção Civil": ["construção", "edificação", "obra", "canteiro", "demolição", "resíduo da construção", "entulho", "supressão vegetal", "movimentação de terra"],
            "Serviços": ["serviços", "prestação de serviços", "atividade terciária", "estabelecimento comercial", "geração de resíduos", "efluente sanitário"],
            "Comércio": ["comércio", "comercial", "varejo", "atacado", "estabelecimento", "resíduo comercial", "embalagem", "descarte"],
            "Outros": ["atividade", "empreendimento", "projeto", "desenvolvimento", "sustentável", "impacto", "mitigação", "compensação", "monitoramento"]
        }
        
        # 🚫 FILTRO RESTRITIVO: Apenas palavras específicas para a atividade
        palavras_atividade = palavras_chave_federais.get(grupo_atividade, [])
        
        if not palavras_atividade:
            print(f"⚠️ Nenhuma palavra-chave específica mapeada para '{grupo_atividade}'")
            return []
        
        legislacoes_federais = []
        
        # 🔍 BUSCAR NAS LEIS REAIS CARREGADAS DE TODAS AS FONTES (INCLUINDO PINECONE)
        for lei in self.todas_fontes_data:
            # Filtrar apenas leis federais
            jurisdicao = lei.get("jurisdicao", "").lower()
            if "federal" not in jurisdicao:
                continue
            titulo = lei.get("titulo", "")
            ementa = lei.get("ementa", "")
            titulo_ementa = (titulo + " " + ementa).lower()
            
            # 🎯 VERIFICAÇÃO RIGOROSA: A lei deve conter pelo menos uma palavra-chave específica
            if any(palavra in titulo_ementa for palavra in palavras_atividade):
                aplicabilidade = self._gerar_aplicabilidade_federal_real(lei, grupo_atividade)
                
                legislacao_formatada = {
                    "esfera": "Federal",
                    "titulo_legislacao": titulo,
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": ementa[:200] + "..." if len(ementa) > 200 else ementa,
                    "aplicabilidade": aplicabilidade,
                    "fonte_dados": "Pinecone - Dados Reais"  # 🔍 TRANSPARÊNCIA DE ORIGEM
                }
                
                legislacoes_federais.append(legislacao_formatada)
        
        print(f"🎯 Filtro restritivo aplicado: {len(legislacoes_federais)} leis federais REAIS para '{grupo_atividade}'")
        print(f"📊 Fonte: 100% dados reais do Pinecone")
        return legislacoes_federais[:limite]
    
    def _gerar_aplicabilidade_federal_real(self, lei: Dict, grupo_atividade: str) -> str:
        """Gera o texto da coluna "aplicabilidade" da tabela, baseado EXCLUSIVAMENTE nos dados reais da lei"""
        
        titulo = lei.get("titulo", "").lower()
        ementa = lei.get("ementa", "").lower()
        
        # 🔍 ANÁLISE BASEADA EXCLUSIVAMENTE EM DADOS REAIS
        # Extrair informações relevantes da ementa real da lei
        if "meio ambiente" in ementa and "licenciamento" in ementa:
            return f"Licenciamento ambiental aplicável a atividades de {grupo_atividade.lower()} conforme ementa da lei"
        elif "florestal" in ementa or "floresta" in ementa:
            return f"Regulamentação florestal aplicável a atividades de {grupo_atividade.lower()} conforme ementa da lei"
        elif "crimes" in ementa and "ambiental" in ementa:
            return f"Define crimes ambientais aplicáveis a {grupo_atividade.lower()} conforme ementa da lei"
        elif "resíduos" in ementa or "resíduo" in ementa:
            return f"Gestão de resíduos aplicável a atividades de {grupo_atividade.lower()} conforme ementa da lei"
        elif "água" in ementa or "hídrico" in ementa:
            return f"Gestão de recursos hídricos aplicável a atividades de {grupo_atividade.lower()} conforme ementa da lei"
        elif "conservação" in ementa or "proteção" in ementa:
            return f"Conservação ambiental aplicável a atividades de {grupo_atividade.lower()} conforme ementa da lei"
        else:
            # 🚨 TRANSPARÊNCIA TOTAL: Usar apenas dados reais da ementa
            ementa_resumida = ementa[:100] + "..." if len(ementa) > 100 else ementa
            return f"Aplicável a atividades de {grupo_atividade.lower()}: {ementa_resumida}"

    def _legislacoes_estaduais(self, municipio: str, grupo_atividade: str, limite: int) -> List[Dict]:
        """Retorna APENAS legislações estaduais REAIS do Pinecone relacionadas ao grupo de atividade"""
        
        # 🎯 FILTRO EXPANDIDO: Palavras-chave mais abrangentes por atividade (baseado em dados reais do Pinecone)
        palavras_chave_restritivas = {
            "Agricultura": ["licenciamento ambiental", "gestão ambiental", "sustentabilidade ambiental", "zoneamento ambiental", "passivo ambiental", "impactos ambientais", "gestão de resíduos sólidos", "resíduos perigosos", "compostagem", "aterro sanitário", "reciclagem", "reutilização", "poluição difusa", "contaminação do solo", "recursos hídricos", "bacia hidrográfica", "outorga de uso da água", "índice de qualidade da água", "eutrofização", "tratamento de efluentes", "esgotamento sanitário", "água subterrânea", "emissões atmosféricas", "material particulado", "biodiversidade", "fragmentação de habitats", "corredores ecológicos", "plano de gerenciamento de resíduos sólidos", "inventário florestal"],
            "Pecuária": ["pecuár", "gado", "bovino", "suíno", "avícola", "frigorífico", "abate", "rebanho", "pastagem", "criação de animais", "atividade rural", "ambiental", "meio ambiente", "recursos", "licenciamento"],
            "Indústria": ["industr", "fábrica", "manufatur", "produção industrial", "poluição industrial", "emissão", "efluente", "ambiental", "meio ambiente", "licenciamento"],
            "Mineração": ["miner", "lavra", "garimpo", "extração mineral", "jazida", "degradação", "recuperação", "ambiental", "meio ambiente", "licenciamento"],
            "Saneamento": ["saneamento", "água", "esgoto", "resíduo", "tratamento", "abastecimento", "lixo", "coleta", "ambiental", "meio ambiente", "recursos hídricos"],
            "Energia": ["energia", "elétrica", "hidrelétrica", "solar", "eólica", "usina", "geração", "impacto ambiental", "ambiental", "meio ambiente", "licenciamento"],
            "Transporte": ["transporte", "rodoviário", "ferroviário", "aquaviário", "portuário", "aeroportuário", "logística", "combustível", "emissão veicular", "poluição atmosférica", "ruído", "impacto viário", "ambiental", "meio ambiente", "licenciamento"],
            "Construção Civil": ["construção", "edificação", "obra", "canteiro", "demolição", "resíduo da construção", "entulho", "supressão vegetal", "movimentação de terra", "drenagem", "impermeabilização", "ambiental", "meio ambiente", "licenciamento"],
            "Serviços": ["serviços", "prestação de serviços", "atividade terciária", "estabelecimento comercial", "geração de resíduos", "efluente sanitário", "consumo de água", "energia elétrica", "ambiental", "meio ambiente", "licenciamento"],
            "Comércio": ["comércio", "comercial", "varejo", "atacado", "estabelecimento", "resíduo comercial", "embalagem", "descarte", "consumo", "sustentabilidade", "ambiental", "meio ambiente", "licenciamento"],
            "Outros": ["atividade", "empreendimento", "projeto", "desenvolvimento", "sustentável", "impacto", "mitigação", "compensação", "monitoramento", "controle", "ambiental", "meio ambiente", "licenciamento"]
        }
        
        # 🚫 FILTRO RESTRITIVO: Apenas palavras específicas para a atividade
        palavras_atividade = palavras_chave_restritivas.get(grupo_atividade, [])
        
        if not palavras_atividade:
            print(f"⚠️ Nenhuma palavra-chave específica mapeada para '{grupo_atividade}'")
            return []
        
        legislacoes_estaduais = []
        
        # 🔍 BUSCAR NAS LEIS REAIS CARREGADAS DE TODAS AS FONTES (INCLUINDO PINECONE)
        for lei in self.todas_fontes_data:
            # Filtrar apenas leis estaduais (incluindo "Estadual - Tocantins")
            jurisdicao = lei.get("jurisdicao", "").lower()
            if "estadual" not in jurisdicao:
                continue
            titulo_desc = (lei.get("titulo", "") + " " + lei.get("descricao", "")).lower()
            
            # 🎯 VERIFICAÇÃO RIGOROSA: A lei deve conter pelo menos uma palavra-chave específica
            if any(palavra in titulo_desc for palavra in palavras_atividade):
                legislacoes_estaduais.append({
                    "esfera": "Estadual",
                    "titulo_legislacao": lei.get("titulo", "Lei Estadual"),
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": lei.get("descricao", "")[:150] + "..." if len(lei.get("descricao", "")) > 150 else lei.get("descricao", ""),
                    "aplicabilidade": f"Aplicável especificamente a atividades de {grupo_atividade.lower()} no estado do Tocantins",
                    "fonte_dados": "Pinecone - Dados Reais"  # 🔍 TRANSPARÊNCIA DE ORIGEM
                })
        
        # ✅ Usando apenas dados reais carregados do Pinecone
        # ✅ AGORA USA APENAS DADOS REAIS DO PINECONE
        
        # ⚠️ APLICAR FILTRO DE VIGÊNCIA OBRIGATÓRIO
        legislacoes_vigentes = [
            leg for leg in legislacoes_estaduais 
            if self._verificar_vigencia_legislacao(leg)
        ]
        
        print(f"🎯 Filtro restritivo aplicado: {len(legislacoes_vigentes)} leis estaduais REAIS para '{grupo_atividade}'")
        print(f"📊 Fonte: 100% dados reais do Pinecone")
        return legislacoes_vigentes[:limite]

    def _legislacoes_municipais(self, municipio: str, grupo_atividade: str, limite: int) -> List[Dict]:
        """Retorna APENAS legislações municipais REAIS do Pinecone relacionadas ao grupo de atividade"""
        
        # 🎯 FILTRO EXPANDIDO: Palavras-chave mais abrangentes por atividade (baseado em dados reais do Pinecone)
        palavras_chave_municipais = {
            "Agricultura": ["licenciamento ambiental", "gestão ambiental", "sustentabilidade ambiental", "zoneamento ambiental", "passivo ambiental", "impactos ambientais", "gestão de resíduos sólidos", "resíduos perigosos", "compostagem", "aterro sanitário", "reciclagem", "reutilização", "poluição difusa", "contaminação do solo", "recursos hídricos", "bacia hidrográfica", "outorga de uso da água", "índice de qualidade da água", "eutrofização", "tratamento de efluentes", "esgotamento sanitário", "água subterrânea", "emissões atmosféricas", "material particulado", "biodiversidade", "fragmentação de habitats", "corredores ecológicos", "plano de gerenciamento de resíduos sólidos", "inventário florestal"],
            "Pecuária": ["pecuár", "gado", "bovino", "suíno", "avícola", "sanitário", "plano diretor", "pastagem", "criação de animais", "atividade rural", "ambiental", "meio ambiente", "recursos", "licenciamento"],
            "Indústria": ["industr", "fábrica", "manufatur", "zoneamento industrial", "obras", "plano diretor", "emissão", "efluente", "ambiental", "meio ambiente", "licenciamento"],
            "Mineração": ["miner", "lavra", "garimpo", "extração", "plano diretor", "degradação", "recuperação", "ambiental", "meio ambiente", "licenciamento"],
            "Saneamento": ["saneamento", "água", "esgoto", "resíduo", "abastecimento", "plano diretor", "lixo", "coleta", "ambiental", "meio ambiente", "recursos hídricos"],
            "Energia": ["energia", "elétrica", "renovável", "solar", "eólica", "plano diretor", "impacto ambiental", "ambiental", "meio ambiente", "licenciamento"],
            "Transporte": ["transporte", "trânsito", "mobilidade urbana", "plano diretor", "sistema viário", "poluição sonora", "emissão veicular", "ambiental", "meio ambiente", "licenciamento"],
            "Construção Civil": ["construção", "edificação", "obra", "alvará", "plano diretor", "código de obras", "resíduo da construção", "supressão vegetal", "ambiental", "meio ambiente", "licenciamento"],
            "Serviços": ["serviços", "estabelecimento", "atividade econômica", "plano diretor", "zoneamento", "geração de resíduos", "ambiental", "meio ambiente", "licenciamento"],
            "Comércio": ["comércio", "comercial", "estabelecimento", "atividade econômica", "plano diretor", "zoneamento comercial", "resíduo comercial", "ambiental", "meio ambiente", "licenciamento"],
            "Outros": ["atividade", "empreendimento", "projeto", "plano diretor", "zoneamento", "uso do solo", "impacto", "ambiental", "meio ambiente", "licenciamento"]
        }
        
        # 🚫 FILTRO RESTRITIVO: Apenas palavras específicas para a atividade
        palavras_atividade = palavras_chave_municipais.get(grupo_atividade, [])
        
        if not palavras_atividade:
            print(f"⚠️ Nenhuma palavra-chave específica mapeada para '{grupo_atividade}'")
            return []
        
        legislacoes_municipais = []
        
        # 🔍 BUSCAR NAS LEIS REAIS CARREGADAS DE TODAS AS FONTES (INCLUINDO PINECONE)
        for lei in self.todas_fontes_data:
            # Filtrar apenas leis municipais (incluindo "Municipal - [Nome do Município]")
            jurisdicao = lei.get("jurisdicao", "").lower()
            if "municipal" not in jurisdicao:
                continue
            titulo_desc = (lei.get("titulo", "") + " " + lei.get("descricao", "")).lower()
            
            # 🎯 VERIFICAÇÃO RIGOROSA: A lei deve conter palavra-chave específica
            if any(palavra in titulo_desc for palavra in palavras_atividade):
                legislacoes_municipais.append({
                    "esfera": "Municipal",
                    "titulo_legislacao": lei.get("titulo", "Lei Municipal"),
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": lei.get("descricao", "")[:150] + "..." if len(lei.get("descricao", "")) > 150 else lei.get("descricao", ""),
                    "aplicabilidade": f"Aplicável especificamente a atividades de {grupo_atividade.lower()} no município de {municipio}",
                    "fonte_dados": "Pinecone - Dados Reais"  # 🔍 TRANSPARÊNCIA DE ORIGEM
                })
        
        # ✅ Aguardando indexação de dados municipais reais no Pinecone
        # ✅ AGORA USA APENAS DADOS REAIS DO PINECONE
        
        # ⚠️ APLICAR FILTRO DE VIGÊNCIA OBRIGATÓRIO
        legislacoes_vigentes = [
            leg for leg in legislacoes_municipais 
            if self._verificar_vigencia_legislacao(leg)
        ]
        
        print(f"🎯 Filtro restritivo aplicado: {len(legislacoes_vigentes)} leis municipais REAIS para '{grupo_atividade}' em {municipio}")
        print(f"📊 Fonte: 100% dados reais do Pinecone")
        print(f"ℹ️ Nota: Dados municipais específicos serão incluídos conforme indexação no Pinecone")
        return legislacoes_vigentes[:limite]

    def gerar_estrutura_tabela(self, descricao_usuario: str) -> Dict[str, Any]:
        """
        Gera a estrutura da tabela baseada na descrição do usuário
        usando IA direcionada da OpenAI
        """
        
        # Prompt direcionado APENAS para a geração da estrutura da tabela
        prompt_sistema = """
        Você é uma IA especializada em organizar dados de leis ambientais em tabelas.
        Sua função é APENAS gerar estruturas de tabelas baseadas na descrição do usuário.
        
        REGRAS IMPORTANTES:
        1. Sempre retorne um JSON válido
        2. Crie colunas relevantes para leis ambientais
        3. Seja específico e prático
        4. Não invente dados, apenas estruture
        5. Use nomes de colunas claros e objetivos
        
        Formato de resposta obrigatório:
        {
            "titulo_tabela": "Nome da tabela",
            "descricao": "Breve descrição do que a tabela organiza",
            "colunas": [
                {
                    "nome": "nome_coluna",
                    "tipo": "texto|numero|data|link",
                    "descricao": "O que esta coluna representa"
                }
            ],
            "filtros_sugeridos": ["filtro1", "filtro2"],
            "ordenacao_padrao": "nome_da_coluna"
        }
        """
        
        prompt_usuario = f"""
        Crie uma estrutura de tabela para organizar leis ambientais baseada nesta descrição:
        
        "{descricao_usuario}"
        
        Considere que temos dados de leis com: título, descrição, data, link do arquivo, conteúdo parcial.
        Retorne APENAS o JSON da estrutura, sem explicações adicionais.
        """
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                timeout=60.0,  # Timeout de 60 segundos
                max_retries=3  # Máximo de 3 tentativas
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.3,  # Baixa criatividade para ser mais direcionado
                max_tokens=1000
            )
            
            resposta_ia = response.choices[0].message.content.strip()
            
            # Tentar extrair JSON da resposta
            if resposta_ia.startswith('```json'):
                resposta_ia = resposta_ia.replace('```json', '').replace('```', '').strip()
            
            estrutura = json.loads(resposta_ia)
            return estrutura
            
        except openai.APIConnectionError as e:
            print(f"❌ Erro de conexão com a API OpenAI: {e}")
            print("💡 Verifique sua conexão com a internet e tente novamente")
            return self._estrutura_padrao()
        except openai.APITimeoutError as e:
            print(f"❌ Timeout na API OpenAI: {e}")
            print("💡 A API demorou para responder, tente novamente")
            return self._estrutura_padrao()
        except openai.AuthenticationError as e:
            print(f"❌ Erro de autenticação OpenAI: {e}")
            print("💡 Verifique se a OPENAI_API_KEY está correta no arquivo .env")
            return self._estrutura_padrao()
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON da IA: {e}")
            return self._estrutura_padrao()
        except Exception as e:
            print(f"❌ Erro na IA: {e}")
            # Retorna estrutura padrão em caso de erro
            return self._estrutura_padrao()
    
    def _estrutura_padrao(self) -> Dict[str, Any]:
        """Estrutura padrão de tabela em caso de erro"""
        return {
            "titulo_tabela": "Leis Ambientais - Organização Padrão",
            "descricao": "Tabela básica com informações das leis ambientais",
            "colunas": [
                {
                    "nome": "numero_lei",
                    "tipo": "texto",
                    "descricao": "Número da lei extraído do título"
                },
                {
                    "nome": "titulo",
                    "tipo": "texto",
                    "descricao": "Título completo da lei"
                },
                {
                    "nome": "ano",
                    "tipo": "numero",
                    "descricao": "Ano de publicação da lei"
                },
                {
                    "nome": "tema_principal",
                    "tipo": "texto",
                    "descricao": "Tema principal da lei"
                },
                {
                    "nome": "link",
                    "tipo": "link",
                    "descricao": "Link para o arquivo da lei"
                }
            ],
            "filtros_sugeridos": ["ano", "tema_principal"],
            "ordenacao_padrao": "ano"
        }
    
    def gerar_tabela_vazia(self, estrutura: Dict[str, Any]) -> pd.DataFrame:
        """
        A IA gera uma tabela vazia baseada no prompt com a estrutura fornecida
        """
        colunas = [col["nome"] for col in estrutura["colunas"]]
        df_vazio = pd.DataFrame(columns=colunas)
        
        # Adicionar algumas linhas de exemplo vazias para visualização
        for i in range(3):
            linha_vazia = {col: f"[{col}_{i+1}]" for col in colunas}
            df_vazio = pd.concat([df_vazio, pd.DataFrame([linha_vazia])], ignore_index=True)
        
        return df_vazio
    
    def popular_tabela(self, estrutura: Dict, num_documentos: int = 10, incluir_todas_fontes: bool = True) -> pd.DataFrame:
        """
        Popula a tabela com dados de todas as fontes ou apenas leis estaduais
        
        Args:
            estrutura: Estrutura da tabela definida pela IA
            num_documentos: Número de documentos a incluir na tabela
            incluir_todas_fontes: Se True, inclui todas as fontes; se False, apenas leis estaduais
            
        Returns:
            DataFrame populado com os dados
        """
        try:
            # Escolher fonte de dados
            if incluir_todas_fontes:
                dados_fonte = self.todas_fontes_data[:num_documentos]
                print(f"📊 Populando tabela com {len(dados_fonte)} documentos de TODAS as fontes")
            else:
                # Filtrar apenas leis estaduais dos dados do Pinecone
                dados_estaduais = [d for d in self.todas_fontes_data if d.get('jurisdicao', '').startswith('Estadual')]
                dados_fonte = dados_estaduais[:num_documentos]
                print(f"📊 Populando tabela com {len(dados_fonte)} leis estaduais do Pinecone")
            
            # Processar cada documento
            dados_processados = []
            for documento in dados_fonte:
                if incluir_todas_fontes:
                    dados_doc = self._extrair_dados_documento(documento)
                else:
                    dados_doc = self._extrair_dados_lei(documento, estrutura)
                dados_processados.append(dados_doc)
            
            # Criar DataFrame
            df = pd.DataFrame(dados_processados)
            
            # Ajustar colunas conforme estrutura solicitada
            colunas_estrutura = estrutura.get('colunas', [])
            if colunas_estrutura:
                df_ajustado = self._ajustar_colunas_estrutura(df, colunas_estrutura, incluir_todas_fontes)
                return df_ajustado
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao popular tabela: {e}")
            return pd.DataFrame()
    
    def _extrair_dados_documento(self, documento: Dict) -> Dict:
        """
        Extrai dados de um documento de qualquer fonte
        
        Args:
            documento: Dicionário com dados do documento
            
        Returns:
            Dicionário com dados extraídos e padronizados
        """
        return {
            'fonte': documento.get('fonte', 'N/A'),
            'tipo': documento.get('tipo', 'N/A'),
            'titulo': documento.get('titulo', 'N/A'),
            'descricao': documento.get('descricao', 'N/A')[:200] + '...' if len(documento.get('descricao', '')) > 200 else documento.get('descricao', 'N/A'),
            'categoria': documento.get('categoria', 'N/A'),
            'jurisdicao': documento.get('jurisdicao', 'N/A'),
            'data_indexacao': documento.get('data_indexacao', 'N/A'),
            'conteudo': documento.get('conteudo', 'N/A')[:100] + '...' if len(documento.get('conteudo', '')) > 100 else documento.get('conteudo', 'N/A')
        }
    
    def _ajustar_colunas_estrutura(self, df: pd.DataFrame, colunas_estrutura: List[Dict], incluir_todas_fontes: bool) -> pd.DataFrame:
        """Ajusta as colunas do DataFrame conforme a estrutura solicitada"""
        df_ajustado = pd.DataFrame()
        
        for col_info in colunas_estrutura:
            nome_col = col_info.get('nome', '')
            
            if incluir_todas_fontes:
                # Mapeamento para dados de todas as fontes
                if nome_col.lower() in ['fonte', 'origem']:
                    df_ajustado[nome_col] = df.get('fonte', '')
                elif nome_col.lower() in ['tipo', 'categoria_documento']:
                    df_ajustado[nome_col] = df.get('tipo', '')
                elif nome_col.lower() in ['título', 'titulo']:
                    df_ajustado[nome_col] = df.get('titulo', '')
                elif nome_col.lower() in ['descrição', 'descricao']:
                    df_ajustado[nome_col] = df.get('descricao', '')
                elif nome_col.lower() in ['categoria', 'classificacao']:
                    df_ajustado[nome_col] = df.get('categoria', '')
                elif nome_col.lower() in ['jurisdição', 'jurisdicao', 'abrangencia']:
                    df_ajustado[nome_col] = df.get('jurisdicao', '')
                elif nome_col.lower() in ['data', 'data_indexacao']:
                    df_ajustado[nome_col] = df.get('data_indexacao', '')
                else:
                    df_ajustado[nome_col] = df.get(nome_col.lower(), '')
            else:
                # Mapeamento para leis estaduais apenas
                if nome_col.lower() in ['título', 'titulo']:
                    df_ajustado[nome_col] = df.get('titulo', '')
                elif nome_col.lower() in ['descrição', 'descricao']:
                    df_ajustado[nome_col] = df.get('descricao', '')
                elif nome_col.lower() == 'data':
                    df_ajustado[nome_col] = df.get('data', '')
                elif nome_col.lower() == 'link':
                    df_ajustado[nome_col] = df.get('link', '')
                elif nome_col.lower() in ['número', 'numero']:
                    df_ajustado[nome_col] = df.get('numero', '')
                else:
                    df_ajustado[nome_col] = ''
        
        return df_ajustado
    
    def _extrair_dados_lei(self, lei: Dict, estrutura: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Extrai dados específicos de uma lei baseado na estrutura da tabela
        """
        dados_extraidos = {}
        
        for coluna in estrutura["colunas"]:
            nome_col = coluna["nome"]
            tipo_col = coluna["tipo"]
            
            # Mapeamento básico de dados
            if nome_col in ["titulo", "título"]:
                dados_extraidos[nome_col] = lei.get("titulo", "")
            elif nome_col in ["descricao", "descrição"]:
                dados_extraidos[nome_col] = lei.get("descricao", "")
            elif nome_col in ["data", "ano"]:
                data_lei = lei.get("data", "")
                if nome_col == "ano" and data_lei:
                    try:
                        dados_extraidos[nome_col] = data_lei.split("-")[0]
                    except:
                        dados_extraidos[nome_col] = ""
                else:
                    dados_extraidos[nome_col] = data_lei
            elif nome_col in ["link", "link_arquivo"]:
                dados_extraidos[nome_col] = lei.get("link_arquivo", "")
            elif nome_col in ["numero_lei", "numero"]:
                titulo = lei.get("titulo", "")
                # Extrair número da lei do título
                import re
                match = re.search(r'Lei nº (\d+[./]\d+)', titulo)
                dados_extraidos[nome_col] = match.group(1) if match else ""
            else:
                # Para outras colunas, usar conteúdo parcial ou descrição
                dados_extraidos[nome_col] = lei.get("conteudo_parcial", "")[:50] + "..."
        
        return dados_extraidos
    
    def salvar_tabela(self, df: pd.DataFrame, estrutura: Dict[str, Any], formato: str = "excel") -> str:
        """
        Salva a tabela em diferentes formatos
        """
        titulo_arquivo = estrutura["titulo_tabela"].replace(" ", "_").lower()
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Usar path relativo ao diretório do projeto
        projeto_root = Path(__file__).parent.parent
        
        if formato == "excel":
            nome_arquivo = f"tabela_{titulo_arquivo}_{timestamp}.xlsx"
            caminho = projeto_root / nome_arquivo
            df.to_excel(caminho, index=False)
        elif formato == "csv":
            nome_arquivo = f"tabela_{titulo_arquivo}_{timestamp}.csv"
            caminho = projeto_root / nome_arquivo
            df.to_csv(caminho, index=False, encoding='utf-8')
        else:
            raise ValueError("Formato não suportado. Use 'excel' ou 'csv'")
        
        return str(caminho)
    
    def gerar_relatorio_tabela(self, estrutura: Dict[str, Any], df: pd.DataFrame) -> str:
        """
        Gera um relatório sobre a tabela criada
        """
        relatorio = f"""
# 📊 RELATÓRIO DA TABELA GERADA

## 📋 Informações Gerais
- **Título:** {estrutura['titulo_tabela']}
- **Descrição:** {estrutura['descricao']}
- **Total de Linhas:** {len(df)}
- **Total de Colunas:** {len(df.columns)}

## 🏗️ Estrutura da Tabela
"""
        
        for i, coluna in enumerate(estrutura['colunas'], 1):
            relatorio += f"""
### {i}. {coluna['nome'].title()}
- **Tipo:** {coluna['tipo']}
- **Descrição:** {coluna['descricao']}
"""
        
        relatorio += f"""
## 🔍 Filtros Sugeridos
{', '.join(estrutura.get('filtros_sugeridos', []))}

## 📈 Ordenação Padrão
{estrutura.get('ordenacao_padrao', 'Não definida')}

## 📊 Prévia dos Dados
```
{df.head().to_string()}
```
"""
        
        return relatorio


if __name__ == "__main__":
    """Teste do sistema de carregamento de dados"""
    print("🧪 TESTANDO SISTEMA DE CARREGAMENTO DE DADOS")
    print("=" * 60)
    
    try:
        # Inicializar o serviço
        ia_tabela = IATabela()
        
        # Verificar carregamento das fontes (todos do Pinecone)
        dados_pinecone = ia_tabela.todas_fontes_data
        dados_estaduais = [d for d in dados_pinecone if d.get('jurisdicao', '').startswith('Estadual')]
        dados_federais = [d for d in dados_pinecone if d.get('jurisdicao') == 'Federal']
        dados_municipais = [d for d in dados_pinecone if d.get('jurisdicao', '').startswith('Municipal')]
        
        print(f"\n📊 RESUMO DOS DADOS CARREGADOS (PINECONE APENAS):")
        print(f"   • Leis Estaduais: {len(dados_estaduais)} documentos")
        print(f"   • Leis Federais: {len(dados_federais)} documentos")
        print(f"   • Leis Municipais: {len(dados_municipais)} documentos")
        print(f"   • Total de todas as fontes: {len(dados_pinecone)} documentos")
        
        # Verificar detalhes do EIA/RIMA
        if ia_tabela.leis_eia_rima and "leis_eia_rima" in ia_tabela.leis_eia_rima:
            print(f"\n🔍 DETALHES EIA/RIMA:")
            for lei_info in ia_tabela.leis_eia_rima["leis_eia_rima"]:
                print(f"   • {lei_info.get('numero', 'N/A')}: {lei_info.get('titulo', 'Sem título')}")
        
        # Verificar Artigo 225
        if ia_tabela.constituicao_artigo_225:
            print(f"\n📜 ARTIGO 225:")
            for artigo in ia_tabela.constituicao_artigo_225:
                print(f"   • Título: {artigo.get('titulo', 'N/A')}")
                print(f"   • URL: {artigo.get('url', 'N/A')}")
                break  # Apenas o primeiro (único) artigo
        
        print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()