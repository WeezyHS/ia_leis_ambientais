import os
import re
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from app.services.pinecone_service import vectorstore
from app.services.custom_prompt import QA_CUSTOM_PROMPT
from app.services.text_normalizer import normalizar_texto, normalizar_pergunta_busca
from app.services.enhanced_retriever import buscar_documentos_com_normalizacao
from app.services.database_stats import detectar_pergunta_tecnica, gerar_resposta_tecnica

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

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": QA_CUSTOM_PROMPT
    }
)

def consultar_lei(pergunta: str) -> dict:
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
            # Formatamos a resposta para incluir o título da lei e seu conteúdo
            conteudo_formatado = []
            for doc in documentos:
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
                for doc in documentos
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
    
    # Busca documentos usando normalização de texto
    documentos_normalizados = buscar_documentos_com_normalizacao(pergunta_enriquecida, k=4)
    
    # Se encontrou documentos com busca normalizada, usa eles
    if documentos_normalizados:
        # Cria contexto a partir dos documentos encontrados
        contexto = "\n\n".join([doc.page_content for doc in documentos_normalizados])
        
        # Usa o prompt customizado para gerar resposta
        prompt_formatado = QA_CUSTOM_PROMPT.format(
            context=contexto,
            question=pergunta
        )
        
        resposta_llm = llm.invoke(prompt_formatado)
        resposta = resposta_llm.content
        documentos = documentos_normalizados
    else:
        # Fallback para busca padrão
        resultado = qa_chain(pergunta_enriquecida)
        resposta = resultado["result"]
        documentos = resultado.get("source_documents", [])

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
        
        # Extrair número da lei do título
        lei_no_titulo = extrair_numero_lei(titulo)
        
        leis_relacionadas.append({
            "titulo": titulo,
            "descricao": descricao,
            "conteudo": conteudo,
            "numero_lei": lei_no_titulo if lei_no_titulo else "N/A"
        })

    return {
        "resposta": resposta,
        "leis_relacionadas": leis_relacionadas
    }
