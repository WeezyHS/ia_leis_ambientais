# Guia de Múltiplas Fontes de Dados

Este sistema permite adicionar facilmente múltiplas fontes de dados para enriquecer sua IA de consulta de leis ambientais.

## 🎯 Fontes Já Configuradas

### 1. Assembleia Legislativa do Tocantins (Atual)
- **URL**: https://www.al.to.leg.br/legislacaoEstadual
- **Tipo**: PDFs de leis estaduais
- **Status**: ✅ Ativo

### 2. Planalto (Federal)
- **URL**: https://www.planalto.gov.br
- **Tipo**: Leis federais ambientais importantes
- **Inclui**: Política Nacional do Meio Ambiente, Código Florestal, etc.
- **Status**: ✅ Configurado

### 3. IBAMA
- **URL**: https://www.ibama.gov.br
- **Tipo**: Normativas e instruções técnicas
- **Status**: ✅ Configurado

## 🚀 Como Usar

### Opção 1: Coletar de Todas as Fontes Configuradas

```bash
python multi_source_indexer.py
```

Este comando irá:
1. Coletar dados de todas as fontes configuradas
2. Processar e filtrar documentos ambientais
3. Indexar automaticamente no Pinecone
4. Criar backup em `backup_multi_source.json`

### Opção 2: Adicionar Fonte Personalizada

#### 2.1 Adicionar de um arquivo JSON

```bash
python add_custom_source.py --source "Ministério do Meio Ambiente" --file meus_documentos.json
```

**Formato do arquivo JSON:**
```json
[
  {
    "text": "Texto completo do documento...",
    "url": "https://exemplo.com/documento1",
    "type": "pdf"
  },
  {
    "text": "Outro documento...",
    "url": "https://exemplo.com/documento2",
    "type": "html"
  }
]
```

#### 2.2 Adicionar de uma URL específica

```bash
# Para PDF
python add_custom_source.py --source "CONAMA" --url "https://exemplo.com/resolucao.pdf"

# Para página HTML
python add_custom_source.py --source "MMA" --url "https://exemplo.com/legislacao.html"
```

#### 2.3 Adicionar texto manualmente

```bash
python add_custom_source.py --source "Fonte Manual" --text "Texto da lei ou normativa..."
```

## 🔧 Adicionando Novas Fontes Permanentes

Para adicionar uma nova fonte que será coletada automaticamente:

### 1. Criar um Novo Scraper

Edite o arquivo `app/services/multi_source_scraper.py` e adicione uma nova classe:

```python
class MeuNovoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Nome da Fonte", "https://site.exemplo.com")
        
    def extract_documents(self) -> List[Dict]:
        # Implementar lógica de coleta
        documents = []
        # ... sua lógica aqui ...
        return documents
        
    def is_relevant_document(self, text: str) -> bool:
        # Implementar filtro de relevância
        keywords = ["ambiental", "ecologia", "sustentabilidade"]
        return any(keyword in text.lower() for keyword in keywords)
```

### 2. Registrar o Novo Scraper

No mesmo arquivo, adicione seu scraper à lista:

```python
class MultiSourceCollector:
    def __init__(self):
        self.scrapers = [
            TocantinsAssembleiaScraper(),
            PlanaltoScraper(),
            IbamaScraper(),
            MeuNovoScraper(),  # ← Adicione aqui
        ]
```

## 📋 Exemplos de Fontes Recomendadas

### Sites Governamentais Brasileiros

1. **Ministério do Meio Ambiente**
   - URL: https://www.gov.br/mma/pt-br
   - Tipo: Portarias, resoluções, políticas

2. **CONAMA**
   - URL: https://www.gov.br/mma/pt-br/assuntos/conama
   - Tipo: Resoluções ambientais

3. **ANA (Agência Nacional de Águas)**
   - URL: https://www.gov.br/ana/pt-br
   - Tipo: Normativas sobre recursos hídricos

4. **ICMBio**
   - URL: https://www.gov.br/icmbio/pt-br
   - Tipo: Instruções normativas sobre conservação

### Sites Estaduais (Exemplos)

1. **CETESB (São Paulo)**
   - URL: https://cetesb.sp.gov.br
   - Tipo: Normas técnicas ambientais

2. **INEA (Rio de Janeiro)**
   - URL: http://www.inea.rj.gov.br
   - Tipo: Deliberações e resoluções

3. **FEAM (Minas Gerais)**
   - URL: http://www.feam.br
   - Tipo: Normativas estaduais

## 🔍 Monitoramento e Logs

O sistema gera logs detalhados durante a coleta:

```
=== Coletando de: Assembleia TO ===
Coletando página 1: https://www.al.to.leg.br/legislacaoEstadual?pagPaginaAtual=1
Processado: Assembleia TO - 15 chunks
Coletados 5 documentos de Assembleia TO

=== Coletando de: Planalto Federal ===
Processado: Planalto Federal - 25 chunks
Coletados 5 documentos de Planalto Federal

Total de documentos coletados: 10
Indexando 40 chunks no Pinecone...
Indexação concluída!
```

## ⚙️ Configurações Avançadas

### Ajustar Tamanho dos Chunks

Edite `multi_source_indexer.py`:

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Aumentar para chunks maiores
    chunk_overlap=300,  # Aumentar sobreposição
    length_function=len,
)
```

### Filtros de Relevância Personalizados

Cada scraper pode ter seus próprios filtros. Edite o método `is_relevant_document()`:

```python
def is_relevant_document(self, text: str) -> bool:
    # Filtros específicos para sua fonte
    environmental_keywords = [
        "licenciamento ambiental",
        "estudo de impacto",
        "gestão de resíduos",
        # ... adicione mais palavras-chave
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in environmental_keywords)
```

## 🚨 Considerações Importantes

1. **Respeite os Termos de Uso**: Sempre verifique os termos de uso dos sites
2. **Rate Limiting**: O sistema inclui delays para não sobrecarregar os servidores
3. **Backup**: Sempre mantenha backups dos dados coletados
4. **Monitoramento**: Acompanhe os logs para identificar problemas
5. **Qualidade**: Revise periodicamente a qualidade dos dados coletados

## 🆘 Solução de Problemas

### Erro de Timeout
```bash
# Aumentar timeout nas configurações do requests
response = requests.get(url, timeout=30)  # Era 20
```

### Selenium não Funciona
```bash
# Verificar se o msedgedriver.exe está no diretório correto
# Baixar versão mais recente se necessário
```

### Muitos Documentos Irrelevantes
```bash
# Ajustar filtros de relevância no método is_relevant_document()
# Adicionar mais palavras-chave específicas
```

### Problemas de Encoding
```bash
# Sempre usar encoding='utf-8' ao salvar arquivos
# Verificar se o site usa encoding diferente
```

## 📞 Suporte

Para adicionar novas fontes ou resolver problemas:

1. Verifique os logs de erro
2. Teste com uma fonte pequena primeiro
3. Valide a qualidade dos dados coletados
4. Monitore o uso da API do Pinecone

---

**Próximos Passos Sugeridos:**

1. Teste o sistema com as fontes já configuradas
2. Adicione uma fonte personalizada simples
3. Monitore a qualidade das respostas da IA
4. Expanda gradualmente para mais fontes
5. Configure monitoramento automático