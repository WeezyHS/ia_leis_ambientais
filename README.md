# Scraper de Normas Ambientais ABNT

Este projeto implementa um scraper automatizado para extrair informações sobre normas ambientais do catálogo da ABNT (Associação Brasileira de Normas Técnicas).

## 🎯 Objetivo

Automatizar a coleta de informações sobre normas técnicas relacionadas ao meio ambiente, sustentabilidade e gestão ambiental disponíveis no catálogo oficial da ABNT.

## 📋 Funcionalidades

- ✅ Busca automatizada por termos ambientais
- ✅ Extração de códigos de normas (NBR, ISO)
- ✅ Coleta de títulos e descrições
- ✅ Identificação de preços
- ✅ Tratamento automático de CAPTCHA
- ✅ Geração de relatórios consolidados
- ✅ Suporte a múltiplos termos de busca

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Selenium WebDriver** - Automação do navegador
- **Chrome/Chromium** - Navegador para scraping
- **JSON** - Armazenamento de dados
- **Regex** - Processamento de texto

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd ia_leis_ambientais
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Instale o ChromeDriver:**
   - Baixe o ChromeDriver compatível com sua versão do Chrome
   - Adicione ao PATH do sistema ou coloque na pasta do projeto

## 🚀 Como Usar

### Uso Básico

```python
from abnt_scraper_final import ABNTScraper

# Inicializa o scraper
scraper = ABNTScraper()

# Realiza busca por um termo
results = scraper.search_and_extract("ambiental")

# Fecha o scraper
scraper.close()
```

### Execução do Script Principal

```bash
python abnt_scraper_final.py
```

Este script irá:
1. Buscar por 7 termos ambientais predefinidos
2. Extrair informações de cada resultado
3. Gerar arquivos HTML e JSON para cada busca
4. Criar um relatório consolidado

### Demonstrações Interativas

```bash
python demo_scraper.py
```

Oferece 4 opções de demonstração:
1. Busca simples por 'ambiental'
2. Busca múltipla (água, resíduos, ar)
3. Análise específica ISO 14000
4. Executar todas as demonstrações

## 📊 Resultados

### Últimos Resultados Obtidos

- **7 termos pesquisados**: ambiental, environmental, sustentabilidade, resíduos, água, ar, solo
- **1.702 produtos encontrados** no total
- **21 normas únicas identificadas**

### Distribuição por Termo:
- **água**: 1.126 produtos
- **solo**: 295 produtos
- **ambiental**: 120 produtos
- **resíduos**: 112 produtos
- **sustentabilidade**: 49 produtos
- **environmental**: 0 produtos
- **ar**: 0 produtos

### Principais Normas Identificadas:
1. **ABNT NBR ISO 14040:2025** - Environmental management - Life cycle assessment
2. **ABNT NBR ISO 14030-3:2025** - Environmental performance evaluation
3. **ABNT PR 2030-1:2024** - Environmental, social and governance (ESG)
4. **ABNT NBR ISO 14001:2015** - Environmental management systems
5. **ABNT NBR 9895:2025** - Environmental passive in soil and groundwater

## 📁 Estrutura de Arquivos

```
ia_leis_ambientais/
├── abnt_scraper_final.py          # Script principal do scraper
├── demo_scraper.py                # Demonstrações interativas
├── generate_report.py             # Gerador de relatórios
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação
├── abnt_consolidated_results.json # Resultados consolidados
├── abnt_report.json              # Relatório detalhado
├── abnt_report.txt               # Relatório legível
└── resultados/                   # Arquivos de resultados individuais
    ├── abnt_results_ambiental.html
    ├── abnt_results_ambiental.json
    └── ...
```

## 🔧 Configuração Avançada

### Parâmetros do Scraper

```python
scraper = ABNTScraper(
    headless=True,          # Execução sem interface gráfica
    max_wait_time=30,       # Tempo máximo de espera (segundos)
    enable_captcha_handling=True  # Tratamento automático de CAPTCHA
)
```

### Termos de Busca Personalizados

```python
termos_personalizados = [
    "gestão ambiental",
    "ISO 14001",
    "sustentabilidade",
    "carbono",
    "emissões"
]

for termo in termos_personalizados:
    results = scraper.search_and_extract(termo)
```

## 🚨 Considerações Importantes

### Limitações
- O site da ABNT pode implementar medidas anti-bot
- CAPTCHA pode aparecer e requer intervenção manual
- Velocidade limitada para evitar sobrecarga do servidor
- Alguns resultados podem não ser capturados devido à estrutura dinâmica da página

### Boas Práticas
- Use delays entre requisições
- Monitore logs para identificar problemas
- Mantenha o ChromeDriver atualizado
- Respeite os termos de uso do site da ABNT

### Tratamento de Erros
- Timeout automático para páginas que não carregam
- Retry automático em caso de falhas temporárias
- Logs detalhados para debugging
- Graceful shutdown em caso de interrupção

## 📈 Análise dos Dados

### Geração de Relatórios

```bash
python generate_report.py
```

Gera:
- `abnt_report.json`: Dados estruturados
- `abnt_report.txt`: Relatório legível

### Análise Estatística

O relatório inclui:
- Contagem total de produtos por termo
- Lista de normas únicas identificadas
- Distribuição de preços (quando disponível)
- Análise temporal das normas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é destinado apenas para fins educacionais e de pesquisa. Respeite os termos de uso do site da ABNT.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs de erro
2. Consulte a documentação do Selenium
3. Abra uma issue no repositório

## 📚 Recursos Adicionais

- [Documentação Selenium](https://selenium-python.readthedocs.io/)
- [Site oficial ABNT](https://www.abnt.org.br/)
- [Catálogo ABNT](https://www.abntcatalogo.com.br/)

---

**Desenvolvido para automatizar a coleta de informações sobre normas ambientais brasileiras** 🌱

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
