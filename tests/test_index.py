# test_index.py

from app.services.indexar import indexar_leis

leis_exemplo = [
    {
        "titulo": "LEI Nº 4.790, DE 21 DE JULHO DE 2025",
        "descricao": "Institui a Semana de Prevenção de Acidentes com Idosos e Orientações de Primeiros Socorros no Estado do Tocantins."
    },
    {
        "titulo": "LEI Nº 4.789, DE 18 DE JULHO DE 2025",
        "descricao": "Dispõe sobre a criação de programas de incentivo à agricultura familiar no Estado do Tocantins."
    }
]

qtd = indexar_leis(leis_exemplo)
print(f"{qtd} leis indexadas com sucesso.")
print("Se você executar este script novamente, nenhuma duplicata será adicionada ao Pinecone.")