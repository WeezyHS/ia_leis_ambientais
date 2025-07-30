from bs4 import BeautifulSoup

def extrair_leis_do_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    leis = []

    # Pega todos os blocos que contêm leis
    blocos = soup.find_all("div", class_="row")

    for bloco in blocos:
        divs = bloco.find_all("div", class_="col-12")
        if len(divs) < 3:
            continue  # Pula blocos incompletos

        # Extrai título
        titulo_tag = divs[0].find("h4")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        # Extrai descrição curta
        descricao_curta_tag = divs[1].find("strong")
        descricao_curta = descricao_curta_tag.get_text(strip=True) if descricao_curta_tag else ""

        # Extrai texto completo da lei
        descricao_completa = divs[2].get_text(strip=True)

        if titulo and (descricao_curta or descricao_completa):
            leis.append({
                "titulo": titulo,
                "descricao": descricao_curta,
                "conteudo": descricao_completa
            })

    return leis
