import json
from app.services.indexar import indexar_leis

with open("tests/leis_100.json", "r", encoding="utf-8") as f:
    leis = json.load(f)

qtd = indexar_leis(leis)
print(f"{qtd} leis indexadas com sucesso (sem duplicações).")
