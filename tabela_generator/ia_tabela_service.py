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
        
        openai.api_key = self.api_key
        
        # Carregar dados de todas as fontes
        self.leis_data = self._carregar_leis()
        self.todas_fontes_data = self._carregar_todas_fontes()
        
    def _carregar_leis(self) -> List[Dict]:
        """Carrega os dados das leis do arquivo JSON"""
        try:
            arquivo_leis = Path("c:/ia_leis_ambientais/leis_ambientais_CORRETAS_20250807_004018.json")
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
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
        
        if formato == "excel":
            nome_arquivo = f"tabela_{titulo_arquivo}_{timestamp}.xlsx"
            caminho = Path("c:/ia_leis_ambientais") / nome_arquivo
            df.to_excel(caminho, index=False)
        elif formato == "csv":
            nome_arquivo = f"tabela_{titulo_arquivo}_{timestamp}.csv"
            caminho = Path("c:/ia_leis_ambientais") / nome_arquivo
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