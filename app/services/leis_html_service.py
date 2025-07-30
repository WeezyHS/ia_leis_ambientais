from bs4 import BeautifulSoup
import re

# Lista de palavras-chave ambientais
PALAVRAS_CHAVE_EXATAS = [
    "estudo de impacto ambiental", "relatório de impacto ambiental",
    "licenciamento ambiental", "gestão ambiental", "sustentabilidade ambiental",
    "zoneamento ambiental", "passivo ambiental", "impactos ambientais",
    "gestão de resíduos sólidos", "resíduos perigosos", "compostagem",
    "aterro sanitário", "reciclagem", "reutilização", "poluição difusa",
    "contaminação do solo", "recursos hídricos", "bacia hidrográfica",
    "outorga de uso da água", "índice de qualidade da água", "eutrofização",
    "tratamento de efluentes", "esgotamento sanitário", "água subterrânea",
    "emissões atmosféricas", "material particulado", "biodiversidade",
    "fragmentação de habitats", "corredores ecológicos",
    "plano de gerenciamento de resíduos sólidos", "inventário florestal"
]

SIGLAS_MAIUSCULAS = ["EIA", "RIMA"]

def normalizar_texto(texto: str) -> str:
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)  # Remove múltiplos espaços
    return texto.strip().lower()

def contem_palavra_chave(texto: str) -> bool:
    texto_normalizado = normalizar_texto(texto)

    # Usa regex para buscar frases completas como palavras isoladas
    for frase in PALAVRAS_CHAVE_EXATAS:
        # Adiciona limites de palavra antes e depois (para evitar palavras encaixadas)
        if re.search(rf'\b{re.escape(frase)}\b', texto_normalizado):
            return True

    # Siglas devem aparecer em CAIXA ALTA exatamente
    for sigla in SIGLAS_MAIUSCULAS:
        if re.search(rf'\b{sigla}\b', texto):
            return True

    return False


def extrair_leis_do_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    leis = []

    blocos = soup.find_all("div", class_="row")
    for bloco in blocos:
        colunas = bloco.find_all("div", class_="col-12")
        if len(colunas) < 3:
            continue

        titulo_tag = colunas[0].find("h4")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        descricao_tag = colunas[1].find("strong")
        descricao = descricao_tag.get_text(strip=True) if descricao_tag else ""

        conteudo = colunas[2].get_text(separator="\n", strip=True)

        texto_completo = f"{titulo}\n{descricao}\n{conteudo}"
        if contem_palavra_chave(texto_completo):
            leis.append({
                "titulo": titulo,
                "descricao": descricao,
                "conteudo": conteudo
            })

    return leis
