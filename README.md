# Sistema Inteligente de Consulta a Leis Ambientais com Múltiplas Fontes

Este projeto oferece um sistema inteligente de busca e consulta de leis ambientais, utilizando técnicas modernas de scraping, vetorização semântica e inteligência artificial. O sistema permite que usuários realizem perguntas em linguagem natural e obtenham respostas precisas com base nas leis indexadas de múltiplas fontes governamentais.

## 🌟 Funcionalidades Principais

### Sistema de Múltiplas Fontes
- **Coleta automatizada** de múltiplas fontes governamentais
- **Fontes pré-configuradas**: Assembleia Legislativa do Tocantins, Planalto, IBAMA
- **Interface web** para gerenciar fontes de dados
- **API REST** para adicionar novas fontes programaticamente
- **Coleta em background** para não bloquear a interface

### Processamento Inteligente
- Extração estruturada de dados: título, descrição e conteúdo completo
- Filtro semântico para selecionar apenas leis ambientais relevantes
- Indexação vetorial no Pinecone para buscas por similaridade semântica
- Geração de embeddings usando o modelo **text-embedding-3-small** da OpenAI
- Integração com GPT-4o-mini para geração de respostas em linguagem natural
- Mecanismo para evitar duplicação de leis no banco vetorial

### Interface e API
- **Interface web moderna** para consultas e gerenciamento
- **API desenvolvida com FastAPI** para upload, consulta e resumo das leis
- **Documentação automática** da API (Swagger/OpenAPI)
- **Suporte a múltiplos formatos**: PDF, HTML, texto direto

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **Selenium** - Automação de navegador para scraping
- **BeautifulSoup** - Parsing de HTML
- **LangChain** - Framework para aplicações com LLM
- **OpenAI API** - Embeddings e geração de texto
- **Pinecone** - Banco de dados vetorial
- **Uvicorn** - Servidor ASGI
- **Requests** - Cliente HTTP para APIs

## 🚀 Como Usar

### 1. Instalação
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd ia_leis_ambientais

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração
Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua_chave_openai
PINECONE_API_KEY=sua_chave_pinecone
PINECONE_ENVIRONMENT=sua_regiao_pinecone
```

### 3. Executar o Sistema
```bash
# Inicie o servidor
uvicorn app.main:app --reload

# Acesse a interface web
# http://localhost:8000
```

## 🌐 Gerenciar Múltiplas Fontes

### Interface Web
1. Acesse `http://localhost:8000`
2. Clique em "🌐 Gerenciar Fontes"
3. Use as abas para:
   - Ver status das fontes
   - Adicionar documentos por URL
   - Adicionar documentos personalizados
   - Coletar dados automaticamente

### Via Scripts Python
```bash
# Coletar de todas as fontes configuradas
python multi_source_indexer.py

# Adicionar fonte personalizada
python add_custom_source.py

# Exemplo específico do CONAMA
python example_conama_scraper.py
```

### Via API REST
```bash
# Verificar status das fontes
curl http://localhost:8000/multi-sources/status

# Adicionar documento por URL
curl -X POST "http://localhost:8000/multi-sources/add-url?url=https://exemplo.com/lei.pdf&source_name=Fonte%20Exemplo"

# Coletar de todas as fontes
curl -X POST http://localhost:8000/multi-sources/collect \
  -H "Content-Type: application/json" \
  -d "{}"
```

## 📚 Fontes de Dados Suportadas

### Pré-configuradas
- **Assembleia Legislativa do Tocantins** - Leis estaduais
- **Planalto** - Leis federais
- **IBAMA** - Normas ambientais federais

### Como Adicionar Novas Fontes
1. **Via Interface Web**: Use a aba "Adicionar Personalizado"
2. **Via Script**: Execute `add_custom_source.py`
3. **Programaticamente**: Crie um novo scraper baseado em `BaseScraper`

### Formatos Suportados
- **PDF** - Extração automática de texto
- **HTML** - Parsing com BeautifulSoup
- **Texto direto** - Inserção manual

## 🔧 Estrutura do Projeto

```
ia_leis_ambientais/
├── app/
│   ├── main.py                 # Aplicação FastAPI principal
│   ├── routes/                 # Rotas da API
│   │   ├── multi_sources.py    # Gerenciamento de múltiplas fontes
│   │   └── ...
│   └── services/               # Serviços de negócio
│       ├── multi_source_scraper.py  # Sistema de scraping modular
│       └── ...
├── static/
│   ├── index.html             # Interface principal
│   └── multi_sources.html     # Interface de gerenciamento
├── multi_source_indexer.py    # Indexador para múltiplas fontes
├── add_custom_source.py       # Script para adicionar fontes
├── example_conama_scraper.py  # Exemplo de scraper específico
├── MULTI_SOURCES_GUIDE.md     # Guia detalhado do sistema
└── requirements.txt           # Dependências
```
