import unicodedata
import re

def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto removendo acentos e padronizando formato.
    Otimizada para performance.
    """
    if not texto:
        return ""
    
    # Operações combinadas para melhor performance
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

# Sets pré-definidos para melhor performance (evita recriar a cada chamada)
PALAVRAS_IRRELEVANTES = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
    'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos',
    'para', 'por', 'com', 'sem', 'sobre', 'entre', 'ate', 'desde',
    'e', 'ou', 'mas', 'porem', 'contudo', 'todavia',
    'que', 'qual', 'quais', 'quando', 'onde', 'como', 'porque',
    'se', 'caso', 'entao', 'assim', 'tambem', 'ja', 'ainda',
    'muito', 'pouco', 'mais', 'menos', 'bem', 'mal',
    'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
    'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo'
}

PALAVRAS_IMPORTANTES = {
    'lei', 'leis', 'artigo', 'artigos', 'paragrafo', 'paragrafos',
    'inciso', 'incisos', 'alinea', 'alineas', 'numero', 'numeros',
    'contem', 'estabelece', 'determina', 'preve', 'dispoe',
    'regulamenta', 'define', 'institui', 'cria', 'altera', 'revoga'
}

def normalizar_pergunta_busca(pergunta: str) -> str:
    """
    Normaliza perguntas de busca mantendo palavras-chave importantes.
    Otimizada para performance com sets pré-definidos.
    """
    pergunta_normalizada = normalizar_texto(pergunta)
    
    # Filtragem otimizada usando list comprehension
    palavras_filtradas = [
        palavra for palavra in pergunta_normalizada.split()
        if palavra in PALAVRAS_IMPORTANTES or 
           (len(palavra) > 3 and palavra not in PALAVRAS_IRRELEVANTES)
    ]
    
    return ' '.join(palavras_filtradas)