# Sistema Inteligente de Consulta a Leis Ambientais do Tocantins

Este projeto tem como objetivo oferecer um sistema inteligente de busca e consulta de leis ambientais do estado do Tocantins, utilizando técnicas modernas de scraping, vetorização semântica e inteligência artificial. O sistema permite que usuários realizem perguntas em linguagem natural e obtenham respostas precisas com base nas leis indexadas.

## Funcionalidades

- Coleta automatizada de leis do site da Assembleia Legislativa do Tocantins (via Selenium).
- Extração estruturada de dados: título, descrição e conteúdo completo da lei.
- Filtro semântico para selecionar apenas leis ambientais relevantes.
- Indexação vetorial no Pinecone para buscas por similaridade semântica.
- API desenvolvida com **FastAPI** para upload, consulta e resumo das leis.
- Geração de embeddings usando o modelo **text-embedding-3-small** da OpenAI.
- Integração com GPT-4o-mini para geração de respostas em linguagem natural.
- Mecanismo para evitar duplicação de leis no banco vetorial.

## Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI**
- **Selenium (Microsoft Edge WebDriver)**
- **BeautifulSoup**
- **LangChain**
- **OpenAI API**
- **Pinecone**
- **dotenv**
- **Uvicorn**
- **Pytest (para testes automatizados)**
