"""
Módulo para filtrar leis revogadas
Otimiza o sistema removendo leis que não são mais aplicáveis
"""

def is_documento_revogado(documento) -> bool:
    """Detecta se um documento foi revogado baseado no conteúdo"""
    if not documento:
        return False
    
    # Se for um dicionário (formato de documento)
    if isinstance(documento, dict):
        texto = documento.get('text', '')
        titulo = documento.get('title', '')
        descricao = documento.get('descricao', '')
        status = documento.get('status', '')
    else:
        # Se for um objeto Document do LangChain
        texto = getattr(documento, 'page_content', str(documento))
        metadata = getattr(documento, 'metadata', {})
        titulo = metadata.get('titulo', '')
        descricao = metadata.get('descricao', '')
        status = metadata.get('status', '')
    
    # Converte tudo para minúsculo para comparação
    textos_para_verificar = [
        str(texto).lower(),
        str(titulo).lower(), 
        str(descricao).lower(),
        str(status).lower()
    ]
    
    # Palavras-chave que indicam revogação
    palavras_revogacao = [
        'revogada', 'revogado', 'revoga',
        '*revogada', '*revogado',
        'ab-rogada', 'ab-rogado',
        'derrogada', 'derrogado',
        'não vigente', 'sem vigência'
    ]
    
    # Verifica se algum texto contém palavras de revogação
    for texto_verificar in textos_para_verificar:
        if any(palavra in texto_verificar for palavra in palavras_revogacao):
            return True
    
    return False

def filtrar_leis_revogadas(documentos):
    """Remove documentos revogados de uma lista"""
    if not documentos:
        return []
    
    documentos_vigentes = []
    documentos_removidos = 0
    
    for doc in documentos:
        if not is_documento_revogado(doc):
            documentos_vigentes.append(doc)
        else:
            documentos_removidos += 1
            # Log opcional para debug
            if isinstance(doc, dict):
                titulo = doc.get('title', doc.get('titulo', 'Sem título'))
            else:
                titulo = getattr(doc, 'metadata', {}).get('titulo', 'Sem título')
            print(f"🗑️ Filtrado documento revogado: {titulo}")
    
    if documentos_removidos > 0:
        print(f"📊 Total filtrado: {documentos_removidos} documentos revogados")
    
    return documentos_vigentes