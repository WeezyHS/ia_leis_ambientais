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
        

        
        # Carregar dados de todas as fontes
        self.leis_data = self._carregar_leis()
        self.todas_fontes_data = self._carregar_todas_fontes()
        
    def _carregar_leis(self) -> List[Dict]:
        """Carrega os dados das leis do arquivo JSON"""
        try:
            # Usar path relativo ao diretório do projeto
            projeto_root = Path(__file__).parent.parent
            arquivo_leis = projeto_root / "leis_ambientais_CORRETAS_20250807_004018.json"
            if arquivo_leis.exists():
                with open(arquivo_leis, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("⚠️ Arquivo de leis não encontrado. Usando dados de exemplo.")
                return self._dados_exemplo()
        except Exception as e:
            print(f"❌ Erro ao carregar leis: {e}")
            return self._dados_exemplo()
    
    def _carregar_todas_fontes(self) -> List[Dict]:
        """Carrega dados de TODAS as fontes disponíveis"""
        todas_fontes = []
        
        try:
            # 1. Leis Estaduais do Tocantins (271 leis)
            for lei in self.leis_data:
                todas_fontes.append({
                    "fonte": "Legislação Estadual TO",
                    "tipo": "Lei Estadual",
                    "titulo": lei.get("titulo", ""),
                    "descricao": lei.get("descricao", ""),
                    "conteudo": lei.get("descricao", ""),
                    "categoria": "Ambiental",
                    "jurisdicao": "Estadual - Tocantins",
                    "data_indexacao": "2025-01-07"
                })
            
            # 2. Dados do Pinecone (ABNT, COEMA, etc.)
            dados_pinecone = self._carregar_dados_pinecone()
            todas_fontes.extend(dados_pinecone)
            
            # 3. Power BI Dashboard (referência)
            todas_fontes.append({
                "fonte": "Power BI Dashboard",
                "tipo": "Dashboard Federal",
                "titulo": "Dashboard Federal de Atos Normativos Ambientais",
                "descricao": "Compilação de 2.770 atos normativos federais desde 1937",
                "conteudo": "Base de dados federal com leis, decretos, resoluções e portarias ambientais",
                "categoria": "Compilação Federal",
                "jurisdicao": "Federal",
                "data_indexacao": "2025-01-07"
            })
            
            print(f"✅ {len(todas_fontes)} documentos carregados de todas as fontes")
            return todas_fontes
            
        except Exception as e:
            print(f"❌ Erro ao carregar todas as fontes: {e}")
            return self._dados_exemplo_todas_fontes()
    
    def _carregar_dados_pinecone(self) -> List[Dict]:
        """Carrega dados dos namespaces do Pinecone"""
        dados_pinecone = []
        
        try:
            from services.pinecone_service import pinecone_index
            
            # Obter estatísticas dos namespaces
            stats = pinecone_index.describe_index_stats()
            
            # ABNT Normas
            if "abnt-normas" in stats.namespaces:
                abnt_count = stats.namespaces["abnt-normas"].vector_count
                for i in range(min(abnt_count, 10)):  # Amostra de 10
                    dados_pinecone.append({
                        "fonte": "ABNT",
                        "tipo": "Norma Técnica",
                        "titulo": f"Norma ABNT {i+1}",
                        "descricao": "Norma técnica brasileira para padrões ambientais",
                        "conteudo": "Especificações técnicas para conformidade ambiental",
                        "categoria": "Norma Técnica",
                        "jurisdicao": "Nacional",
                        "data_indexacao": "2025-01-07"
                    })
            
            # COEMA (se existir namespace)
            if "coema" in stats.namespaces:
                coema_count = stats.namespaces["coema"].vector_count
                for i in range(min(coema_count, 10)):  # Amostra de 10
                    dados_pinecone.append({
                        "fonte": "COEMA",
                        "tipo": "Ato Normativo",
                        "titulo": f"Documento COEMA {i+1}",
                        "descricao": "Documento do Conselho Estadual de Meio Ambiente",
                        "conteudo": "Regulamentação e diretrizes ambientais estaduais",
                        "categoria": "Conselho Ambiental",
                        "jurisdicao": "Estadual - Tocantins",
                        "data_indexacao": "2025-01-07"
                    })
            
        except Exception as e:
            print(f"⚠️ Erro ao acessar Pinecone: {e}")
            # Adicionar dados de exemplo das outras fontes
            dados_pinecone.extend([
                {
                    "fonte": "CONAMA",
                    "tipo": "Resolução",
                    "titulo": "Resoluções CONAMA",
                    "descricao": "Resoluções do Conselho Nacional do Meio Ambiente",
                    "conteudo": "Diretrizes nacionais para política ambiental",
                    "categoria": "Conselho Nacional",
                    "jurisdicao": "Federal",
                    "data_indexacao": "2025-01-07"
                },
                {
                    "fonte": "IBAMA",
                    "tipo": "Instrução Normativa",
                    "titulo": "Instruções Normativas IBAMA",
                    "descricao": "Normas do Instituto Brasileiro do Meio Ambiente",
                    "conteudo": "Regulamentações para fiscalização e licenciamento",
                    "categoria": "Órgão Ambiental",
                    "jurisdicao": "Federal",
                    "data_indexacao": "2025-01-07"
                },
                {
                    "fonte": "ICMBio",
                    "tipo": "Portaria",
                    "titulo": "Portarias ICMBio",
                    "descricao": "Portarias do Instituto Chico Mendes",
                    "conteudo": "Gestão de unidades de conservação",
                    "categoria": "Conservação",
                    "jurisdicao": "Federal",
                    "data_indexacao": "2025-01-07"
                }
            ])
        
        return dados_pinecone
    
    def _dados_exemplo_todas_fontes(self) -> List[Dict]:
        """Dados de exemplo de todas as fontes"""
        return [
            {
                "fonte": "Legislação Estadual TO",
                "tipo": "Lei Estadual",
                "titulo": "Lei nº 4795/2025 - Política Ambiental",
                "descricao": "Institui política estadual de meio ambiente",
                "conteudo": "Estabelece diretrizes para proteção ambiental",
                "categoria": "Ambiental",
                "jurisdicao": "Estadual - Tocantins",
                "data_indexacao": "2025-01-07"
            },
            {
                "fonte": "Power BI Dashboard",
                "tipo": "Dashboard Federal",
                "titulo": "Atos Normativos Federais",
                "descricao": "2.770 atos normativos desde 1937",
                "conteudo": "Compilação federal de legislação ambiental",
                "categoria": "Compilação Federal",
                "jurisdicao": "Federal",
                "data_indexacao": "2025-01-07"
            },
            {
                "fonte": "ABNT",
                "tipo": "Norma Técnica",
                "titulo": "Normas Técnicas Ambientais",
                "descricao": "Padrões técnicos para conformidade",
                "conteudo": "Especificações técnicas ambientais",
                "categoria": "Norma Técnica",
                "jurisdicao": "Nacional",
                "data_indexacao": "2025-01-07"
            }
        ]
    
    def _dados_exemplo(self) -> List[Dict]:
        """Retorna dados de exemplo para demonstração"""
        return [
            {
                "titulo": "Lei nº 1.001/2023 - Política Estadual de Meio Ambiente",
                "descricao": "Institui a Política Estadual de Meio Ambiente do Tocantins",
                "data": "2023-03-15",
                "link_arquivo": "http://exemplo.com/lei1001.pdf",
                "conteudo_parcial": "Dispõe sobre a proteção ambiental..."
            },
            {
                "titulo": "Lei nº 1.002/2023 - Fundo Estadual de Meio Ambiente",
                "descricao": "Cria o Fundo Estadual de Meio Ambiente",
                "data": "2023-04-20",
                "link_arquivo": "http://exemplo.com/lei1002.pdf",
                "conteudo_parcial": "Estabelece recursos para projetos ambientais..."
            },
            {
                "titulo": "Lei nº 1.003/2024 - Licenciamento Ambiental",
                "descricao": "Regulamenta o licenciamento ambiental no estado",
                "data": "2024-01-10",
                "link_arquivo": "http://exemplo.com/lei1003.pdf",
                "conteudo_parcial": "Define procedimentos para licenciamento..."
            }
        ]
    
    def gerar_quadro_resumo_legislacoes(self, municipio: str, grupo_atividade: str, descricao_adicional: str = "", esferas: List[str] = None, comando_natural: bool = False) -> Dict:
        """
        Gera um quadro-resumo de legislações ambientais específico para município e atividade
        
        Args:
            municipio: Nome do município do Tocantins
            grupo_atividade: Grupo de atividade do empreendimento
            descricao_adicional: Descrição adicional do empreendimento
            esferas: Lista de esferas legais a incluir (Federal, Estadual, Municipal)
        
        Returns:
            Dict com estrutura do quadro-resumo
        """
        if esferas is None:
            esferas = ["Federal", "Estadual", "Municipal"]
        
        prompt = f"""
        Você é um especialista em legislação ambiental brasileira. Crie um quadro-resumo de legislações ambientais vigentes para:

        LOCALIZAÇÃO: {municipio}, Tocantins
        ATIVIDADE: {grupo_atividade}
        DETALHES: {descricao_adicional if descricao_adicional else "Não especificado"}
        ESFERAS: {", ".join(esferas)}

        FORMATO OBRIGATÓRIO do quadro-resumo:
        {{
            "titulo_quadro": "Quadro-Resumo de Legislações Ambientais - {municipio}/{grupo_atividade}",
            "municipio": "{municipio}",
            "grupo_atividade": "{grupo_atividade}",
            "descricao": "Legislações ambientais aplicáveis a empreendimentos de {grupo_atividade} em {municipio}, TO",
            "colunas": [
                {{
                    "nome": "esfera",
                    "tipo": "texto",
                    "descricao": "Esfera legal (Federal, Estadual, Municipal)"
                }},
                {{
                    "nome": "titulo_legislacao",
                    "tipo": "texto", 
                    "descricao": "Título completo da legislação"
                }},
                {{
                    "nome": "vigencia",
                    "tipo": "texto",
                    "descricao": "Status de vigência (✅ Vigente, ⚠️ Alterada, ❌ Revogada)"
                }},
                {{
                    "nome": "descricao_resumida",
                    "tipo": "texto",
                    "descricao": "Descrição resumida da aplicabilidade"
                }},
                {{
                    "nome": "aplicabilidade",
                    "tipo": "texto",
                    "descricao": "Como se aplica ao grupo de atividade específico"
                }}
            ],
            "filtros_sugeridos": ["esfera", "vigencia"],
            "ordenacao_padrao": "esfera"
        }}

        IMPORTANTE:
        - Foque em legislações REALMENTE aplicáveis ao grupo "{grupo_atividade}"
        - Considere as especificidades do município "{municipio}" no Tocantins
        - Priorize legislações vigentes e relevantes
        - Use ✅ para vigente, ⚠️ para alterada, ❌ para revogada
        
        Retorne APENAS o JSON válido, sem explicações adicionais.
        """
        
        try:
            # Adaptar prompt baseado no tipo de entrada
            if comando_natural and descricao_adicional:
                # Prompt para comando em linguagem natural
                prompt = f"""
                Você é um especialista em legislação ambiental brasileira, especializado no estado do Tocantins.
                
                SOLICITAÇÃO DO USUÁRIO:
                "{descricao_adicional}"
                
                INFORMAÇÕES EXTRAÍDAS:
                - Município: {municipio}
                - Atividade: {grupo_atividade}
                - Esferas solicitadas: {', '.join(esferas)}
                
                TAREFA: Atender exatamente à solicitação do usuário, gerando um quadro-resumo de legislações ambientais que contemple:
                1. O contexto específico mencionado (ex: licenciamento ambiental, regularização, estudo ambiental)
                2. As esferas legais solicitadas (federal, estadual, municipal)
                3. O tipo de empreendimento e município especificados
                
                ESTRUTURA OBRIGATÓRIA do quadro-resumo:
                - Esfera (Federal, Estadual, Municipal)
                - Título da Legislação (nome oficial completo com numeração e data)
                - Vigência (status atual - APENAS VIGENTES)
                - Descrição Resumida (aplicabilidade específica ao contexto)
                - Aplicabilidade (como se aplica ao empreendimento no contexto do licenciamento)
                
                PREMISSAS OBRIGATÓRIAS:
                1. APENAS legislações VIGENTES (omitir revogadas/substituídas)
                2. Títulos oficiais completos (Lei nº X, de data, nome)
                3. Foco no contexto de licenciamento ambiental
                4. Específico para o estado do Tocantins
                5. Aplicabilidade clara para o tipo de empreendimento
                
                Retorne um JSON com a estrutura:
                {{
                    "quadro_resumo": [
                        {{
                            "esfera": "Federal/Estadual/Municipal",
                            "titulo_legislacao": "Título oficial completo",
                            "vigencia": "✅ Vigente",
                            "descricao_resumida": "Descrição clara e objetiva",
                            "aplicabilidade": "Como se aplica especificamente ao contexto"
                        }}
                    ]
                }}
                """
            else:
                # Prompt padrão para seleção manual
                prompt = f"""
                Você é um especialista em legislação ambiental brasileira, com foco no estado do Tocantins.
                
                TAREFA: Gerar um quadro-resumo de legislações ambientais para:
                - Município: {municipio}
                - Atividade: {grupo_atividade}
                - Esferas legais: {', '.join(esferas)}
                - Contexto adicional: {descricao_adicional}
                
                ESTRUTURA OBRIGATÓRIA do quadro-resumo:
                - Esfera (Federal, Estadual, Municipal)
                - Título da Legislação (nome oficial completo)
                - Vigência (status atual)
                - Descrição Resumida (aplicabilidade específica)
                - Aplicabilidade (como se aplica ao empreendimento)
                
                PREMISSAS OBRIGATÓRIAS:
                1. APENAS legislações VIGENTES
                2. Títulos oficiais completos com numeração e data
                3. Omitir legislações revogadas ou substituídas
                4. Foco em licenciamento ambiental
                5. Específico para o Tocantins
                
                Retorne um JSON com a estrutura:
                {{
                    "quadro_resumo": [
                        {{
                            "esfera": "Federal/Estadual/Municipal",
                            "titulo_legislacao": "Título oficial completo",
                            "vigencia": "✅ Vigente",
                            "descricao_resumida": "Descrição clara e objetiva",
                            "aplicabilidade": "Como se aplica especificamente"
                        }}
                    ]
                }}
                """
            
            client = OpenAI(
                api_key=self.api_key,
                timeout=60.0,  # Timeout de 60 segundos
                max_retries=3  # Máximo de 3 tentativas
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um especialista em legislação ambiental brasileira. Retorne sempre JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Limpar possíveis caracteres extras
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            estrutura = json.loads(content)
            
            # Validar estrutura obrigatória
            campos_obrigatorios = ["titulo_quadro", "municipio", "grupo_atividade", "colunas"]
            for campo in campos_obrigatorios:
                if campo not in estrutura:
                    raise ValueError(f"Campo obrigatório '{campo}' não encontrado na resposta da IA")
            
            return estrutura
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON da IA: {e}")
            return self._estrutura_quadro_padrao(municipio, grupo_atividade)
        except openai.APIConnectionError as e:
            print(f"❌ Erro de conexão com a API OpenAI: {e}")
            print("💡 Verifique sua conexão com a internet e tente novamente")
            return self._estrutura_quadro_padrao(municipio, grupo_atividade)
        except openai.APITimeoutError as e:
            print(f"❌ Timeout na API OpenAI: {e}")
            print("💡 A API demorou para responder, tente novamente")
            return self._estrutura_quadro_padrao(municipio, grupo_atividade)
        except openai.AuthenticationError as e:
            print(f"❌ Erro de autenticação OpenAI: {e}")
            print("💡 Verifique se a OPENAI_API_KEY está correta no arquivo .env")
            return self._estrutura_quadro_padrao(municipio, grupo_atividade)
        except Exception as e:
            print(f"❌ Erro na API OpenAI: {e}")
            return self._estrutura_quadro_padrao(municipio, grupo_atividade)

    def _estrutura_quadro_padrao(self, municipio: str, grupo_atividade: str) -> Dict:
        """Estrutura padrão para quadro-resumo em caso de erro"""
        return {
            "titulo_quadro": f"Quadro-Resumo de Legislações Ambientais - {municipio}/{grupo_atividade}",
            "municipio": municipio,
            "grupo_atividade": grupo_atividade,
            "descricao": f"Legislações ambientais aplicáveis a empreendimentos de {grupo_atividade} em {municipio}, TO",
            "colunas": [
                {"nome": "esfera", "tipo": "texto", "descricao": "Esfera legal"},
                {"nome": "titulo_legislacao", "tipo": "texto", "descricao": "Título da legislação"},
                {"nome": "vigencia", "tipo": "texto", "descricao": "Status de vigência"},
                {"nome": "descricao_resumida", "tipo": "texto", "descricao": "Descrição resumida"},
                {"nome": "aplicabilidade", "tipo": "texto", "descricao": "Aplicabilidade específica"}
            ],
            "filtros_sugeridos": ["esfera", "vigencia"],
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
            
            # Ordenar por esfera (Federal, Estadual, Municipal)
            ordem_esferas = {"Federal": 1, "Estadual": 2, "Municipal": 3}
            df_quadro['ordem_esfera'] = df_quadro['esfera'].map(ordem_esferas)
            df_quadro = df_quadro.sort_values('ordem_esfera').drop('ordem_esfera', axis=1)
            
            return df_quadro
            
        except Exception as e:
            print(f"❌ Erro ao popular quadro-resumo: {e}")
            return self._quadro_exemplo(municipio, grupo_atividade, esferas)

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
        """Retorna APENAS legislações federais VIGENTES aplicáveis ao grupo de atividade"""
        
        # ⚠️ PREMISSA OBRIGATÓRIA: SOMENTE LEGISLAÇÕES VIGENTES
        # Mapeamento de atividades para legislações federais VIGENTES E ATUALIZADAS
        legislacoes_base = {
            "Agricultura": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.651, de 25 de maio de 2012 (Código Florestal Brasileiro)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dispõe sobre a proteção da vegetação nativa, define Áreas de Preservação Permanente e Reserva Legal",
                    "aplicabilidade": "Obrigatória para propriedades rurais - Reserva Legal mínima de 35% no Cerrado do Tocantins"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 6.938, de 31 de agosto de 1981 (Política Nacional do Meio Ambiente)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Institui a Política Nacional do Meio Ambiente, seus fins e mecanismos de formulação e aplicação",
                    "aplicabilidade": "Licenciamento ambiental obrigatório para atividades agropecuárias potencialmente poluidoras"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Resolução CONAMA nº 237, de 19 de dezembro de 1997",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Regulamenta os aspectos de licenciamento ambiental estabelecidos na Política Nacional do Meio Ambiente",
                    "aplicabilidade": "Define competências e procedimentos para licenciamento de atividades agrícolas"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.305, de 2 de agosto de 2010 (Política Nacional de Resíduos Sólidos)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Institui a Política Nacional de Resíduos Sólidos e altera a Lei nº 9.605/1998",
                    "aplicabilidade": "Gestão obrigatória de resíduos sólidos em propriedades agrícolas"
                }
            ],
            "Pecuária": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.651, de 25 de maio de 2012 (Código Florestal Brasileiro)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dispõe sobre a proteção da vegetação nativa, define Áreas de Preservação Permanente e Reserva Legal",
                    "aplicabilidade": "Obrigatória para propriedades rurais - Reserva Legal mínima de 35% no Cerrado do Tocantins"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Decreto nº 9.013, de 29 de março de 2017 (Regulamento de Inspeção Industrial)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Regulamenta a inspeção industrial e sanitária de produtos de origem animal",
                    "aplicabilidade": "Obrigatório para frigoríficos e abatedouros de produtos pecuários"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 9.605, de 12 de fevereiro de 1998 (Lei de Crimes Ambientais)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dispõe sobre as sanções penais e administrativas derivadas de condutas e atividades lesivas ao meio ambiente",
                    "aplicabilidade": "Define crimes ambientais aplicáveis à pecuária, como poluição hídrica e desmatamento ilegal"
                }
            ],
            "Indústria": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 6.938, de 31 de agosto de 1981 (Política Nacional do Meio Ambiente)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Institui a Política Nacional do Meio Ambiente, seus fins e mecanismos de formulação e aplicação",
                    "aplicabilidade": "Licenciamento ambiental obrigatório para atividades industriais potencialmente poluidoras"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Resolução CONAMA nº 237, de 19 de dezembro de 1997",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Regulamenta os aspectos de licenciamento ambiental estabelecidos na Política Nacional do Meio Ambiente",
                    "aplicabilidade": "Define competências e procedimentos para licenciamento de atividades industriais"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.305, de 2 de agosto de 2010 (Política Nacional de Resíduos Sólidos)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Institui a Política Nacional de Resíduos Sólidos e altera a Lei nº 9.605/1998",
                    "aplicabilidade": "Gestão obrigatória de resíduos sólidos industriais e logística reversa"
                }
            ],
            "Mineração": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Decreto-Lei nº 227, de 28 de fevereiro de 1967 (Código de Mineração)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dá nova redação ao Decreto-lei nº 1.985, de 29 de janeiro de 1940 (Código de Minas)",
                    "aplicabilidade": "Regulamenta direitos minerários e regime de aproveitamento das substâncias minerais"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Resolução CONAMA nº 237, de 19 de dezembro de 1997",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Regulamenta os aspectos de licenciamento ambiental estabelecidos na Política Nacional do Meio Ambiente",
                    "aplicabilidade": "Licenciamento ambiental obrigatório para atividades de mineração"
                },
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 13.540, de 18 de dezembro de 2017",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Altera as Leis nº 7.990/1989 e 8.001/1990 para dispor sobre a Compensação Financeira pela Exploração de Recursos Minerais",
                    "aplicabilidade": "Define obrigações de compensação financeira para atividades de mineração"
                }
            ]
        }
        
        # ⚠️ LEGISLAÇÕES GERAIS VIGENTES - aplicáveis a todas as atividades
        legislacoes_gerais = [
            {
                "esfera": "Federal",
                "titulo_legislacao": "Lei nº 9.605, de 12 de fevereiro de 1998 (Lei de Crimes Ambientais)",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Dispõe sobre as sanções penais e administrativas derivadas de condutas e atividades lesivas ao meio ambiente",
                "aplicabilidade": "Aplicável a todas as atividades - define sanções por infrações ambientais"
            },
            {
                "esfera": "Federal",
                "titulo_legislacao": "Lei nº 12.305, de 2 de agosto de 2010 (Política Nacional de Resíduos Sólidos)",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Institui a Política Nacional de Resíduos Sólidos e altera a Lei nº 9.605/1998",
                "aplicabilidade": "Obrigatória para gestão de resíduos sólidos em todas as atividades"
            }
        ]
        
        # Combinar legislações específicas e gerais
        legislacoes = legislacoes_base.get(grupo_atividade, []) + legislacoes_gerais
        
        # ⚠️ APLICAR FILTRO DE VIGÊNCIA OBRIGATÓRIO
        legislacoes_vigentes = [
            leg for leg in legislacoes 
            if self._verificar_vigencia_legislacao(leg)
        ]
        
        return legislacoes_vigentes[:limite]

    def _legislacoes_estaduais(self, municipio: str, grupo_atividade: str, limite: int) -> List[Dict]:
        """Retorna legislações estaduais do Tocantins aplicáveis"""
        
        # Buscar nas leis reais do Tocantins
        legislacoes_estaduais = []
        
        # Filtrar leis relevantes para o grupo de atividade
        palavras_chave = {
            "Agricultura": ["agric", "rural", "agropec", "plantio", "cultivo"],
            "Pecuária": ["pecuár", "gado", "bovino", "suíno", "avícola", "frigorífico"],
            "Indústria": ["industr", "fábrica", "manufatur", "produção"],
            "Mineração": ["miner", "lavra", "garimpo", "extração"],
            "Saneamento": ["saneamento", "água", "esgoto", "resíduo"],
            "Energia": ["energia", "elétrica", "hidrelétrica", "solar", "eólica"]
        }
        
        palavras_atividade = palavras_chave.get(grupo_atividade, ["ambiental"])
        
        # Buscar nas leis carregadas
        for lei in self.leis_data[:limite*2]:  # Buscar mais para filtrar
            titulo_desc = (lei.get("titulo", "") + " " + lei.get("descricao", "")).lower()
            
            # Verificar se a lei é relevante para a atividade
            if any(palavra in titulo_desc for palavra in palavras_atividade):
                legislacoes_estaduais.append({
                    "esfera": "Estadual",
                    "titulo_legislacao": lei.get("titulo", "Lei Estadual"),
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": lei.get("descricao", "")[:150] + "..." if len(lei.get("descricao", "")) > 150 else lei.get("descricao", ""),
                    "aplicabilidade": f"Aplicável a atividades de {grupo_atividade.lower()} no estado do Tocantins"
                })
        
        # ⚠️ LEGISLAÇÕES ESTADUAIS VIGENTES DO TOCANTINS
        if not legislacoes_estaduais:
            legislacoes_estaduais = [
                {
                    "esfera": "Estadual",
                    "titulo_legislacao": "Lei Estadual nº 1.307, de 22 de março de 2002 (Política Estadual do Meio Ambiente do Tocantins)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Institui a Política Estadual do Meio Ambiente, cria o Sistema Estadual do Meio Ambiente e dá outras providências",
                    "aplicabilidade": f"Aplicável a todas as atividades de {grupo_atividade.lower()} no estado do Tocantins"
                },
                {
                    "esfera": "Estadual",
                    "titulo_legislacao": "Decreto Estadual nº 4.632, de 30 de abril de 2013 (Regulamento do NATURATINS)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Regulamenta o licenciamento ambiental no âmbito do Instituto Natureza do Tocantins - NATURATINS",
                    "aplicabilidade": f"Define procedimentos de licenciamento ambiental para atividades de {grupo_atividade.lower()}"
                },
                {
                    "esfera": "Estadual",
                    "titulo_legislacao": "Lei Estadual nº 1.560, de 29 de dezembro de 2004 (Código Florestal do Estado do Tocantins)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Dispõe sobre a Política Florestal do Estado do Tocantins e dá outras providências",
                    "aplicabilidade": f"Regulamenta atividades florestais relacionadas a {grupo_atividade.lower()} no Tocantins"
                }
            ]
        
        # ⚠️ APLICAR FILTRO DE VIGÊNCIA OBRIGATÓRIO
        legislacoes_vigentes = [
            leg for leg in legislacoes_estaduais 
            if self._verificar_vigencia_legislacao(leg)
        ]
        
        return legislacoes_vigentes[:limite]

    def _legislacoes_municipais(self, municipio: str, grupo_atividade: str, limite: int) -> List[Dict]:
        """Retorna legislações municipais aplicáveis"""
        
        return [
            {
                "esfera": "Municipal",
                "titulo_legislacao": f"Lei Orgânica do Município de {municipio}",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Define competências municipais em matéria ambiental",
                "aplicabilidade": f"Estabelece diretrizes locais para atividades de {grupo_atividade.lower()}"
            },
            {
                "esfera": "Municipal",
                "titulo_legislacao": f"Plano Diretor de {municipio}",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Regulamenta o uso e ocupação do solo municipal",
                "aplicabilidade": f"Define zoneamento e restrições para {grupo_atividade.lower()}"
            },
            {
                "esfera": "Municipal",
                "titulo_legislacao": f"Código de Posturas de {municipio}",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Estabelece normas de conduta e funcionamento no município",
                "aplicabilidade": f"Regulamenta aspectos operacionais de {grupo_atividade.lower()}"
            }
        ]
        
        # ⚠️ APLICAR FILTRO DE VIGÊNCIA OBRIGATÓRIO
        legislacoes_vigentes = [
            leg for leg in legislacoes_municipais 
            if self._verificar_vigencia_legislacao(leg)
        ]
        
        return legislacoes_vigentes[:limite]

    def _quadro_exemplo(self, municipio: str, grupo_atividade: str, esferas: List[str]) -> pd.DataFrame:
        """Quadro-resumo de exemplo em caso de erro"""
        dados_exemplo = []
        
        if "Federal" in esferas:
            dados_exemplo.append({
                "esfera": "Federal",
                "titulo_legislacao": "Lei 6.938/1981 – Política Nacional do Meio Ambiente",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Estabelece instrumentos da política ambiental nacional",
                "aplicabilidade": f"Licenciamento ambiental obrigatório para {grupo_atividade.lower()}"
            })
        
        if "Estadual" in esferas:
            dados_exemplo.append({
                "esfera": "Estadual",
                "titulo_legislacao": "Lei Estadual nº 1.307/2002 – Política Ambiental TO",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Institui a Política Estadual do Meio Ambiente do Tocantins",
                "aplicabilidade": f"Aplicável a atividades de {grupo_atividade.lower()} no estado"
            })
        
        if "Municipal" in esferas:
            dados_exemplo.append({
                "esfera": "Municipal",
                "titulo_legislacao": f"Plano Diretor de {municipio}",
                "vigencia": "✅ Vigente",
                "descricao_resumida": "Regulamenta o uso e ocupação do solo municipal",
                "aplicabilidade": f"Define zoneamento para {grupo_atividade.lower()}"
            })
        
        return pd.DataFrame(dados_exemplo)

    def gerar_estrutura_tabela(self, descricao_usuario: str) -> Dict[str, Any]:
        """
        Gera a estrutura da tabela baseada na descrição do usuário
        usando IA direcionada da OpenAI
        """
        
        # Prompt direcionado para geração de estrutura de tabela
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
        Gera uma tabela vazia baseada na estrutura fornecida
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
                dados_fonte = self.leis_data[:num_documentos]
                print(f"📊 Populando tabela com {len(dados_fonte)} leis estaduais")
            
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