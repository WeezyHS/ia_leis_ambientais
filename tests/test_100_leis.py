from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import json
from app.services.leis_html_service import extrair_leis_do_html
import time

options = Options()
# options.add_argument("--headless")  # se quiser rodar invisível
options.add_argument("--disable-gpu")

driver = webdriver.Edge(options=options)
leis_coletadas = []

try:
    for pagina in range(1, 6):
        url = f"https://www.al.to.leg.br/legislacaoEstadual?pagPaginaAtual={pagina}"
        driver.get(url)

        # Pequeno tempo de espera para garantir renderização mínima
        time.sleep(2)

        html = driver.page_source
        with open("tests/exemplo_pagina.html", "w", encoding="utf-8") as f:
            f.write(html)

        leis = extrair_leis_do_html(html)
        leis_coletadas.extend(leis)
finally:
    driver.quit()

print(f"Total de leis extraídas: {len(leis_coletadas)}")

if leis_coletadas:
    with open("tests/leis_100.json", "w", encoding="utf-8") as f:
        json.dump(leis_coletadas, f, ensure_ascii=False, indent=2)
else:
    print("Nenhuma lei extraída. JSON não foi sobrescrito.")
