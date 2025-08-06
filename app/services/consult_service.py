import os
import re
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from app.services.pinecone_service import vectorstore, search_similar_documents
from app.services.custom_prompt import QA_CUSTOM_PROMPT
from app.services.text_normalizer import normalizar_texto, normalizar_pergunta_busca
from app.services.enhanced_retriever import buscar_documentos_com_normalizacao
from app.services.database_stats import detectar_pergunta_tecnica, gerar_resposta_tecnica
from app.services.coema_service import COEMAService
from app.services.lei_filter import filtrar_leis_revogadas

def extrair_numero_lei(pergunta: str):
    # Captura formatos com ou sem ponto, com ou sem espaços
    # Padrões possíveis: "lei 3.519", "lei nº 3519", "lei número 3.519", "lei n° 3519", "lei n.º 3.519"
    # Também captura menções como "lei estadual 3.519" ou "lei ambiental 3.519"
    match = re.search(r"lei(?:\s+(?:estadual|ambiental|municipal|federal))?(?:\s+(?:n[°º\.]?|n[°º\.]?\s*[º°]|n[úu]mero))?\s*(\d{4,5}|\d{1,2}\.\d{3})", pergunta.lower())
    if match:
        numero = match.group(1)
        if '.' in numero:
            return numero  # Já está no formato correto
        # Corrige número sem ponto
        if len(numero) == 4:
            return f"{numero[0]}.{numero[1:]}"     # 3519 → 3.519
        elif len(numero) == 5:
            return f"{numero[:2]}.{numero[2:]}"    # 12345 → 12.345
    return None

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Instância do serviço COEMA
coema_service = COEMAService()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": QA_CUSTOM_PROMPT
    }
)

def detectar_saudacao(pergunta: str) -> bool:
    """Detecta se a mensagem é apenas uma saudação simples"""
    saudacoes = [
        "olá", "oi", "bom dia", "boa tarde", "boa noite", "hello", "hi",
        "tudo bem", "como vai", "e aí", "salve", "hey", "opa"
    ]
    
    pergunta_lower = pergunta.lower().strip()
    
    # Se for uma saudação simples (curta) sem outras palavras relevantes
    if len(pergunta_lower) < 50 and any(saudacao in pergunta_lower for saudacao in saudacoes):
        # Verifica se não contém palavras relacionadas a leis
        palavras_leis = ["lei", "decreto", "resolução", "ambiental", "tocantins", "coema"]
        if not any(palavra in pergunta_lower for palavra in palavras_leis):
            return True
    
    return False

def gerar_resposta_saudacao() -> str:
    """Gera uma resposta amigável para saudações"""
    return """Olá! 👋 

Sou a IA especializada em **Leis Ambientais do Tocantins**, da **Plêiade Ambiental**. 

🌿 Posso ajudá-lo com:
• Consultas sobre leis ambientais específicas
• Informações sobre licenciamento ambiental
• Dados do COEMA (Conselho Estadual do Meio Ambiente)
• Regulamentações e decretos ambientais

Como posso ajudá-lo hoje?"""



def consultar_lei(pergunta: str) -> dict:
    # 🤝 Verifica se é apenas uma saudação
    if detectar_saudacao(pergunta):
        return {
            "resposta": gerar_resposta_saudacao(),
            "leis_relacionadas": [],
            "tipo_resposta": "saudacao"
        }
    
    # 🔧 Verifica se é uma pergunta técnica sobre o sistema
    if detectar_pergunta_tecnica(pergunta):
        resposta_tecnica = gerar_resposta_tecnica(pergunta)
        return {
            "resposta": resposta_tecnica,
            "leis_relacionadas": [],
            "tipo_resposta": "tecnica"
        }
    
    # Normaliza a pergunta para melhorar a busca
    pergunta_normalizada = normalizar_pergunta_busca(pergunta)
    numero_lei = extrair_numero_lei(pergunta)

    # 🔍 Busca por número específico
    if numero_lei:
        # Usa tanto a pergunta original quanto a normalizada para busca por número
        query_busca = f"lei {numero_lei} {pergunta_normalizada}"
        documentos = vectorstore.similarity_search(
            query=query_busca,
            k=5,
            filter={
                "$or": [
                    {"numero_lei": numero_lei},
                    {"numero_lei_puro": numero_lei.replace(".", "")}
                ]
            }
        )

        if documentos:
            # 🗑️ Filtra leis revogadas
            documentos_vigentes = filtrar_leis_revogadas(documentos)
            
            if not documentos_vigentes:
                return {
                    "resposta": f"A Lei {numero_lei} foi encontrada, mas está **revogada** e não é mais aplicável. Para consultas sobre legislação vigente, tente uma busca mais ampla sobre o tema.",
                    "leis_relacionadas": []
                }
            
            # Formatamos a resposta para incluir o título da lei e seu conteúdo
            conteudo_formatado = []
            for doc in documentos_vigentes:
                titulo = doc.metadata.get("titulo", "Sem título")
                descricao = doc.metadata.get("descricao", "")
                conteudo_formatado.append(f"**{titulo}**\n\n{descricao}\n\n{doc.page_content}")
            
            resposta = f"# Lei {numero_lei}\n\nAs informações da Lei {numero_lei} são:\n\n" + "\n\n---\n\n".join(conteudo_formatado)
            
            leis_relacionadas = [
                {
                    "titulo": doc.metadata.get("titulo", "Sem título"),
                    "descricao": doc.metadata.get("descricao", ""),
                    "conteudo": doc.page_content,
                    "numero_lei": numero_lei
                }
                for doc in documentos_vigentes
            ]
            return {
                "resposta": resposta,
                "leis_relacionadas": leis_relacionadas
            }

    # 🤖 Caso não tenha número ou não encontrou diretamente
    # Usa busca aprimorada com normalização para capturar variações de acentuação
    pergunta_enriquecida = pergunta_normalizada
    if numero_lei:
        pergunta_enriquecida = f"Sobre a Lei {numero_lei}: {pergunta_normalizada}"
    
    # Busca documentos usando a nova função que inclui ABNT
    resultados_busca = search_similar_documents(pergunta_enriquecida, top_k=8)
    
    # Converte resultados para formato compatível
    documentos_normalizados = []
    for resultado in resultados_busca:
        # Cria um objeto similar ao Document do LangChain
        class SearchDocument:
            def __init__(self, content, metadata):
                self.page_content = content
                self.metadata = metadata
        
        doc = SearchDocument(
            content=resultado['texto'],
            metadata={
                **resultado['metadado'],
                'tipo_fonte': resultado.get('tipo', 'LEI'),
                'score': resultado.get('score', 0)
            }
        )
        documentos_normalizados.append(doc)
    
    # 🗑️ Filtra leis revogadas
    documentos_normalizados = filtrar_leis_revogadas(documentos_normalizados)
    
    # 🏛️ Busca também no COEMA
    documentos_coema = []
    try:
        resultados_coema = coema_service.search_coema_documents(pergunta_enriquecida, top_k=2)
        if resultados_coema:
            # Converte resultados do COEMA para formato compatível
            for resultado in resultados_coema:
                # Cria um objeto similar ao Document do LangChain
                class COEMADocument:
                    def __init__(self, content, metadata):
                        self.page_content = content
                        self.metadata = metadata
                
                doc_coema = COEMADocument(
                    content=resultado['content'],
                    metadata={
                        **resultado['metadata'],
                        'fonte': 'COEMA',
                        'score': resultado['score']
                    }
                )
                documentos_coema.append(doc_coema)
    except Exception as e:
        print(f"Erro ao buscar no COEMA: {e}")
    
    # Combina documentos das diferentes fontes
    todos_documentos = documentos_normalizados + documentos_coema
    
    # 🗑️ Filtra leis revogadas dos documentos combinados
    todos_documentos = filtrar_leis_revogadas(todos_documentos)
    
    # Se encontrou documentos, usa eles
    if todos_documentos:
        # Cria contexto a partir dos documentos encontrados
        contexto = "\n\n".join([doc.page_content for doc in todos_documentos])
        
        # Usa o prompt customizado para gerar resposta
        prompt_formatado = QA_CUSTOM_PROMPT.format(
            context=contexto,
            question=pergunta
        )
        
        resposta_llm = llm.invoke(prompt_formatado)
        resposta = resposta_llm.content
        documentos = todos_documentos
    else:
        # Fallback para busca padrão
        resultado = qa_chain(pergunta_enriquecida)
        resposta = resultado["result"]
        documentos = resultado.get("source_documents", [])
        
        # 🗑️ Filtra leis revogadas do fallback
        documentos = filtrar_leis_revogadas(documentos)

    # Extraímos os números das leis citadas na resposta para destacar
    numeros_leis_citadas = set()
    for doc in documentos:
        titulo = doc.metadata.get("titulo", "")
        lei_no_titulo = extrair_numero_lei(titulo)
        if lei_no_titulo:
            numeros_leis_citadas.add(lei_no_titulo)
    
    # Adicionamos uma seção de leis consultadas se houver leis citadas
    if numeros_leis_citadas:
        resposta += "\n\n**Leis consultadas:** " + ", ".join([f"Lei {num}" for num in sorted(numeros_leis_citadas)])

    # Preparamos as leis relacionadas com informações mais completas
    leis_relacionadas = []
    for doc in documentos:
        titulo = doc.metadata.get("titulo", "Sem título")
        descricao = doc.metadata.get("descricao", "")
        conteudo = doc.page_content
        fonte = doc.metadata.get("fonte", "Legislação")
        tipo_fonte = doc.metadata.get("tipo_fonte", "LEI")
        
        # Extrair número da lei do título (para leis tradicionais)
        lei_no_titulo = extrair_numero_lei(titulo)
        
        # Para documentos ABNT, usar o código ABNT como identificador
        if tipo_fonte == "ABNT" or "ABNT" in titulo or "NBR" in titulo:
            # Extrair código ABNT do título ou metadados
            codigo_abnt = doc.metadata.get("codigo", "")
            if not codigo_abnt and titulo:
                # Tentar extrair código do título
                import re
                match = re.search(r'(ABNT\s+NBR\s+[A-Z]*\s*\d+(?:[-:]\d+)?)', titulo)
                if match:
                    codigo_abnt = match.group(1)
            
            # Usar código ABNT como número da lei
            if codigo_abnt:
                lei_no_titulo = codigo_abnt
            
            # Adicionar identificação ABNT no título se não estiver presente
            if not titulo.startswith("[ABNT]") and not "ABNT" in titulo:
                titulo = f"[ABNT] {titulo}"
        
        # Adiciona identificação da fonte se for COEMA
        elif fonte == "COEMA":
            titulo = f"[COEMA] {titulo}"
        
        leis_relacionadas.append({
            "titulo": titulo,
            "descricao": descricao,
            "conteudo": conteudo,
            "numero_lei": lei_no_titulo if lei_no_titulo else "N/A",
            "fonte": fonte
        })

    return {
        "resposta": resposta,
        "leis_relacionadas": leis_relacionadas
    }
