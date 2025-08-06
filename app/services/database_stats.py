from app.services.pinecone_service import vectorstore
from typing import Dict, Any
import re

def obter_estatisticas_banco() -> Dict[str, Any]:
    """
    Obtém estatísticas do banco de dados de leis.
    
    Returns:
        Dict com informações sobre o banco de dados
    """
    try:
        # Busca uma amostra grande de documentos para análise
        docs_amostra = vectorstore.similarity_search("lei", k=1000)
        
        # Estatísticas básicas
        total_documentos = len(docs_amostra)
        
        # Análise de leis únicas (por número)
        leis_unicas = set()
        anos_leis = set()
        tipos_documento = {"lei": 0, "decreto": 0, "resolucao": 0, "outros": 0}
        
        for doc in docs_amostra:
            titulo = doc.metadata.get("titulo", "").lower()
            
            # Extrai número da lei
            numero_lei = doc.metadata.get("numero_lei")
            if numero_lei:
                leis_unicas.add(numero_lei)
            
            # Extrai ano da lei (busca por padrões de data mais específicos)
            # Procura por padrões como "de 2023", "/2023", "ano 2023", etc.
            match_ano = re.search(r'(?:de\s+|/|ano\s+|em\s+)((19|20)\d{2})\b', titulo)
            if match_ano:
                anos_leis.add(match_ano.group(1))
            else:
                # Fallback: busca por ano no final do título ou após vírgula
                match_ano_alt = re.search(r',\s*((19|20)\d{2})\b|((19|20)\d{2})\s*$', titulo)
                if match_ano_alt:
                    ano = match_ano_alt.group(1) or match_ano_alt.group(3)
                    anos_leis.add(ano)
            
            # Classifica tipo de documento
            if "lei" in titulo:
                tipos_documento["lei"] += 1
            elif "decreto" in titulo:
                tipos_documento["decreto"] += 1
            elif "resolução" in titulo or "resolucao" in titulo:
                tipos_documento["resolucao"] += 1
            else:
                tipos_documento["outros"] += 1
        
        # Calcula estatísticas
        ano_mais_antigo = min(anos_leis) if anos_leis else "N/A"
        ano_mais_recente = max(anos_leis) if anos_leis else "N/A"
        
        return {
            "total_documentos": total_documentos,
            "total_leis_unicas": len(leis_unicas),
            "periodo_cobertura": {
                "ano_inicio": ano_mais_antigo,
                "ano_fim": ano_mais_recente,
                "total_anos": len(anos_leis)
            },
            "tipos_documento": tipos_documento,
            "banco_dados": {
                "nome": "Pinecone Vector Database",
                "modelo_embedding": "text-embedding-3-small (OpenAI)",
                "dimensoes": "1536 dimensões",
                "tipo": "Banco vetorial para busca semântica"
            }
        }
        
    except Exception as e:
        return {
            "erro": f"Erro ao obter estatísticas: {str(e)}",
            "total_documentos": 0,
            "total_leis_unicas": 0
        }

def gerar_resposta_tecnica(pergunta: str) -> str:
    """
    Gera resposta para perguntas técnicas sobre o sistema.
    
    Args:
        pergunta: Pergunta do usuário
        
    Returns:
        Resposta formatada sobre aspectos técnicos
    """
    stats = obter_estatisticas_banco()
    
    pergunta_lower = pergunta.lower()
    
    # Respostas para diferentes tipos de perguntas técnicas
    if any(palavra in pergunta_lower for palavra in ["quantas leis", "quantidade", "número de leis"]):
        return f"""📊 **Estatísticas do Banco de Dados**

🏛️ **Total de Leis Únicas**: {stats.get('total_leis_unicas', 'N/A')} leis diferentes
📄 **Total de Documentos**: {stats.get('total_documentos', 'N/A')} segmentos de texto indexados

📅 **Período de Cobertura**: {stats.get('periodo_cobertura', {}).get('ano_inicio', 'N/A')} - {stats.get('periodo_cobertura', {}).get('ano_fim', 'N/A')}

**Tipos de Documentos**:
• Leis: {stats.get('tipos_documento', {}).get('lei', 0)}
• Decretos: {stats.get('tipos_documento', {}).get('decreto', 0)}
• Resoluções: {stats.get('tipos_documento', {}).get('resolucao', 0)}
• Outros: {stats.get('tipos_documento', {}).get('outros', 0)}"""

    elif any(palavra in pergunta_lower for palavra in ["banco de dados", "database", "tecnologia"]):
        return f"""🔧 **Informações Técnicas do Sistema**

💾 **Banco de Dados**: {stats.get('banco_dados', {}).get('nome', 'N/A')}
🤖 **Modelo de IA**: {stats.get('banco_dados', {}).get('modelo_embedding', 'N/A')}
📐 **Dimensões**: {stats.get('banco_dados', {}).get('dimensoes', 'N/A')}
🔍 **Tipo**: {stats.get('banco_dados', {}).get('tipo', 'N/A')}

📊 **Dados Indexados**: {stats.get('total_leis_unicas', 'N/A')} leis em {stats.get('total_documentos', 'N/A')} segmentos"""

    elif any(palavra in pergunta_lower for palavra in ["como funciona", "funcionamento", "arquitetura"]):
        return f"""⚙️ **Como o Sistema Funciona**

**Processo de Indexação**:
1. **Coleta**: Scraping automatizado do site da Assembleia Legislativa
2. **Processamento**: Extração e limpeza do texto das leis
3. **Vetorização**: Conversão em embeddings usando IA da OpenAI
4. **Armazenamento**: Indexação no Pinecone para busca semântica

**Processo de Consulta**:
1. **Normalização**: Sua pergunta é processada e normalizada
2. **Busca Semântica**: Encontra leis similares usando vetores
3. **IA Generativa**: GPT-4o-mini gera resposta contextualizada
4. **Resposta**: Retorna informação precisa com citações

📈 **Dados Atuais**: {stats.get('total_leis_unicas', 'N/A')} leis indexadas"""

    else:
        return f"""🤖 **Sistema de Leis Ambientais do Tocantins**

Sim, tenho acesso a um banco de dados especializado! 

**Resumo dos Dados**:
• **{stats.get('total_leis_unicas', 'N/A')} leis únicas** indexadas
• **{stats.get('total_documentos', 'N/A')} segmentos** de texto processados
• **Período**: {stats.get('periodo_cobertura', {}).get('ano_inicio', 'N/A')} a {stats.get('periodo_cobertura', {}).get('ano_fim', 'N/A')}

🔧 **Tecnologia**: Banco vetorial Pinecone + IA OpenAI para busca semântica inteligente

Posso responder perguntas específicas sobre qualquer lei ambiental do Tocantins!"""

def detectar_pergunta_tecnica(pergunta: str) -> bool:
    """
    Detecta se a pergunta é sobre aspectos técnicos do sistema.
    
    Args:
        pergunta: Pergunta do usuário
        
    Returns:
        True se for pergunta técnica, False caso contrário
    """
    # Primeiro verifica se é uma saudação simples
    saudacoes = [
        "olá", "oi", "bom dia", "boa tarde", "boa noite", "hello", "hi",
        "tudo bem", "como vai", "e aí", "salve", "hey"
    ]
    
    pergunta_lower = pergunta.lower().strip()
    
    # Se for apenas uma saudação simples, não é pergunta técnica
    if any(saudacao in pergunta_lower for saudacao in saudacoes) and len(pergunta_lower) < 50:
        return False
    
    # Verifica se contém termos legais/ambientais - se sim, NÃO é pergunta técnica
    termos_legais = [
        "licenciamento", "ambiental", "lei", "decreto", "resolução", "coema",
        "meio ambiente", "florestal", "sustentável", "impacto ambiental",
        "eia", "rima", "averbação", "compensação", "multa", "infração",
        "órgão ambiental", "ibama", "icmbio", "naturatins", "conama"
    ]
    
    # Se contém termos legais, não é pergunta técnica sobre o sistema
    if any(termo in pergunta_lower for termo in termos_legais):
        return False
    
    # Palavras técnicas específicas sobre o SISTEMA (não sobre legislação)
    palavras_tecnicas_sistema = [
        "banco de dados", "database", "quantas leis", "quantidade de leis", 
        "número de leis", "tecnologia", "arquitetura", "dados indexados", 
        "informações técnicas", "estatísticas", "você tem acesso", "possui dados", 
        "disponível no sistema", "indexadas", "armazenadas", "como o sistema funciona",
        "funcionamento do sistema", "como funciona o sistema", "sistema funciona"
    ]
    
    # Verifica se é especificamente sobre o sistema, não sobre temas legais
    return any(palavra in pergunta_lower for palavra in palavras_tecnicas_sistema)