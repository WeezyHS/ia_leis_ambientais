import json

with open("tests/leis.json", encoding="utf-8") as f:
    leis = json.load(f)

print(f"Quantidade de leis no arquivo: {len(leis)}")