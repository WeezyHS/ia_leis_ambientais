import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pypdf
import io
from tqdm import tqdm # Para a barra de progresso

# --- Configuração do LangChain e Serviços ---
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

# --- Configuração do Selenium ---
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Carrega as variáveis do arquivo .env
load_dotenv()
print("Chaves de API carregadas com sucesso.")

URL_ALVO = "https://www.al.to.leg.br/legislacaoEstadual"
PINECONE_INDEX_NAME = "leis-ambientais" # O nome do seu index no Pinecone

# Inicializa os clientes das APIs (fazemos isso uma vez)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm_classificador = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def encontrar_todos_os_links():
    """Navega por todas as páginas e coleta todos os links de PDF."""
    todos_os_links = []
    # No futuro, podemos aumentar o range para 251 para pegar todas as páginas
    for i in range(1, 4): # Para teste, continuamos com as 3 primeiras páginas
        url_pagina = f"{URL_ALVO}?pagPaginaAtual={i}"
        print(f"\nAnalisando página {i}: {url_pagina}")
        
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        driver = webdriver.Edge(service=EdgeService(executable_path="msedgedriver.exe"), options=options)
        try:
            driver.get(url_pagina)
            time.sleep(10)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            links_na_pagina = []
            for link in soup.find_all('a', href=True):
                if link['href'].startswith('/arquivo/'):
                    url_completa = requests.compat.urljoin(URL_ALVO, link['href'])
                    if url_completa not in links_na_pagina:
                        links_na_pagina.append(url_completa)
            
            if not links_na_pagina:
                print(f"Nenhum link encontrado na página {i}, parando a busca.")
                break
            
            todos_os_links.extend(links_na_pagina)
            print(f"Encontrados {len(links_na_pagina)} links na página {i}.")
            time.sleep(3)
        finally:
            driver.quit()
            
    return list(set(todos_os_links))

def extrair_texto_do_pdf(pdf_url):
    """Baixa um PDF de uma URL e extrai seu texto."""
    try:
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()
        
        # Usa um buffer de memória para ler o PDF sem salvar em disco
        pdf_file = io.BytesIO(response.content)
        reader = pypdf.PdfReader(pdf_file)
        
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() or ""
            
        return texto_completo
    except Exception as e:
        print(f"  - Erro ao processar PDF da URL {pdf_url}: {e}")
        return None

def is_lei_ambiental(texto):
    """Usa a IA para classificar se um texto é sobre lei ambiental."""
    if not texto or len(texto) < 50:
        return False
        
    prompt = f"""
    O seguinte texto é o início de um documento legal. 
    Ele trata sobre direito ambiental, ecologia, meio ambiente, recursos hídricos, fauna, flora ou temas diretamente relacionados?
    Responda apenas com 'SIM' ou 'NÃO'.

    TEXTO:
    "{texto[:1500]}" 
    """ # Usamos apenas os primeiros 1500 caracteres para uma classificação rápida e barata
    
    resposta = llm_classificador.invoke(prompt)
    return "sim" in resposta.content.lower()

def processar_e_salvar_pdf(pdf_url):
    """Orquestra o processo completo para um único PDF."""
    print(f"\nProcessando: {pdf_url}")
    
    # 1. Extrair Texto
    texto = extrair_texto_do_pdf(pdf_url)
    if not texto:
        return
        
    # 2. Classificar
    print("  - Classificando relevância do tema...")
    if not is_lei_ambiental(texto):
        print("  - REJEITADO: Não parece ser uma lei ambiental.")
        return
        
    print("  - ACEITO: Lei ambiental relevante. Fatiando e salvando...")
    
    # 3. Fatiar (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(texto)
    
    # 4. Vetorizar e Salvar no Pinecone
    # LangChain cuida do embedding e do envio para o Pinecone
    PineconeVectorStore.from_texts(
        texts=chunks, 
        embedding=embeddings, 
        index_name=PINECONE_INDEX_NAME,
        metadatas=[{"source": pdf_url}] * len(chunks) # Adiciona a URL de origem como metadado
    )
    print(f"  - SUCESSO: Documento salvo no Pinecone em {len(chunks)} pedaços.")


# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    # Primeiro, encontramos todos os links
    links_para_processar = encontrar_todos_os_links()
    
    if links_para_processar:
        print(f"\n--- INICIANDO PROCESSAMENTO DE {len(links_para_processar)} DOCUMENTOS ---")
        # Usamos o tqdm para criar uma barra de progresso no terminal
        for link in tqdm(links_para_processar, desc="Processando PDFs"):
            processar_e_salvar_pdf(link)
            time.sleep(3) # Pausa de 3s para respeitar limites de API
            
        print("\n--- PROCESSAMENTO CONCLUÍDO ---")
    else:
        print("Nenhum link de PDF foi encontrado para processar.")