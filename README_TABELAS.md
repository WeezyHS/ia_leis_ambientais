# 📊 IA DIRECIONADA - GERADOR DE TABELAS DE LEIS AMBIENTAIS

## 🎯 Objetivo

Sistema de **IA direcionada** que utiliza a API da OpenAI de forma programática para gerar tabelas/planilhas organizadas das leis ambientais do Tocantins. Diferente de uma IA conversacional, esta é uma **IA focada e direcionada** especificamente para organização tabular de dados.

## 🤖 Características da IA Direcionada

- **🎯 Focada**: Especializada apenas em organização de tabelas
- **📋 Programática**: Usa prompts estruturados e direcionados
- **⚡ Eficiente**: Respostas rápidas e consistentes
- **🔧 Configurável**: Adapta-se à descrição do usuário
- **📊 Estruturada**: Sempre retorna dados organizados

## 🏗️ Estrutura do Sistema

```
tabela_generator/
├── __init__.py                 # Módulo principal
├── ia_tabela_service.py        # Serviço de IA direcionada
├── interface_tabela.py         # Interface CLI
└── web_interface.py            # Interface web (Streamlit)

Scripts de execução:
├── executar_tabela_cli.py      # Executa interface CLI
├── executar_tabela_web.py      # Executa interface web
└── teste_tabela_simples.py     # Teste básico
```

## 🚀 Como Usar

### 1. **Teste Simples (Recomendado para começar)**
```bash
python teste_tabela_simples.py
```
- Demonstra o funcionamento básico
- Gera uma tabela vazia de exemplo
- Mostra os dados disponíveis

### 2. **Interface de Linha de Comando**
```bash
python executar_tabela_cli.py
```
- Interface interativa no terminal
- Menu com opções claras
- Ideal para uso rápido

### 3. **Interface Web (Streamlit)**
```bash
python executar_tabela_web.py
```
- Interface gráfica moderna
- Visualização em tempo real
- Download direto das tabelas

## 📋 Funcionalidades

### ✅ **Geração de Estrutura Inteligente**
- Analisa a descrição do usuário
- Cria colunas relevantes automaticamente
- Define tipos de dados apropriados
- Sugere filtros e ordenação

### ✅ **Dois Modos de Operação**
1. **Tabela Vazia**: Apenas estrutura para preenchimento manual
2. **Tabela Populada**: Preenchida com dados reais das leis

### ✅ **Múltiplos Formatos de Saída**
- **Excel** (.xlsx) - Ideal para análise
- **CSV** (.csv) - Compatibilidade universal
- **JSON** (.json) - Estrutura de dados
- **Markdown** (.md) - Relatórios

### ✅ **Relatórios Automáticos**
- Estatísticas da tabela gerada
- Descrição das colunas
- Sugestões de uso

## 💡 Exemplos de Descrições

### **Organizacionais**
- "Organizar leis por ano e tema principal"
- "Agrupar por órgão responsável e tipo de lei"
- "Tabela cronológica com foco em datas"

### **Temáticas**
- "Foco em licenciamento ambiental"
- "Leis sobre recursos hídricos"
- "Regulamentações de resíduos sólidos"

### **Analíticas**
- "Comparar leis antes e depois de 2020"
- "Análise de frequência por tema"
- "Evolução legislativa por década"

## 🔧 Configuração

### **Pré-requisitos**
1. **Python 3.8+**
2. **OpenAI API Key** configurada no `.env`
3. **Dependências instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

### **Arquivo .env**
```env
OPENAI_API_KEY=sua_chave_aqui
```

## 📊 Dados Disponíveis

O sistema trabalha com **271 leis ambientais** filtradas e corretas do Tocantins, contendo:

- **📄 Título**: Nome completo da lei
- **📝 Descrição**: Resumo do conteúdo
- **📅 Data**: Data de publicação
- **🔗 Link**: URL para o arquivo PDF
- **📋 Conteúdo**: Trecho do texto da lei

## 🎯 Exemplos de Uso

### **Exemplo 1: Tabela por Ano**
```
Descrição: "Organizar leis por ano de publicação"

Resultado:
┌─────┬──────────────────────────────┬──────┬─────────────┐
│ Ano │ Título                       │ Tema │ Link        │
├─────┼──────────────────────────────┼──────┼─────────────┤
│2024 │ Lei nº 1.003 - Licenciamento │ Amb. │ link.pdf    │
│2023 │ Lei nº 1.002 - Fundo Amb.    │ Fin. │ link2.pdf   │
└─────┴──────────────────────────────┴──────┴─────────────┘
```

### **Exemplo 2: Tabela Temática**
```
Descrição: "Foco em licenciamento ambiental"

Resultado:
┌──────────────┬─────────────┬─────────────┬──────────────┐
│ Tipo Licença │ Órgão Resp. │ Prazo       │ Observações  │
├──────────────┼─────────────┼─────────────┼──────────────┤
│ LP           │ NATURATINS  │ 5 anos      │ Prévia       │
│ LI           │ NATURATINS  │ 6 anos      │ Instalação   │
└──────────────┴─────────────┴─────────────┴──────────────┘
```

## 🔍 Como Funciona a IA Direcionada

### **1. Análise da Descrição**
```python
# A IA recebe um prompt estruturado:
prompt = """
Você é uma IA especializada em organizar dados de leis ambientais.
Crie uma estrutura de tabela baseada nesta descrição:
"{descrição_do_usuário}"
"""
```

### **2. Geração de Estrutura**
```json
{
  "titulo_tabela": "Nome da Tabela",
  "colunas": [
    {
      "nome": "ano",
      "tipo": "numero",
      "descricao": "Ano de publicação"
    }
  ],
  "filtros_sugeridos": ["ano", "tema"],
  "ordenacao_padrao": "ano"
}
```

### **3. População com Dados**
- Extrai informações das leis reais
- Mapeia para as colunas definidas
- Aplica formatação apropriada

## 📈 Vantagens da IA Direcionada

### **🎯 Vs. IA Conversacional**
| IA Direcionada | IA Conversacional |
|----------------|-------------------|
| ✅ Focada em tabelas | ❌ Genérica |
| ✅ Respostas consistentes | ❌ Variável |
| ✅ Estrutura previsível | ❌ Formato livre |
| ✅ Rápida | ❌ Pode ser lenta |
| ✅ Programática | ❌ Interativa |

### **⚡ Benefícios**
- **Velocidade**: Respostas em segundos
- **Consistência**: Sempre retorna estruturas válidas
- **Precisão**: Focada no objetivo específico
- **Escalabilidade**: Processa múltiplas solicitações
- **Confiabilidade**: Menos propensa a erros

## 🛠️ Personalização

### **Modificar Prompts**
Edite `ia_tabela_service.py` para ajustar o comportamento:

```python
prompt_sistema = """
Suas instruções personalizadas aqui...
"""
```

### **Adicionar Novos Tipos de Coluna**
```python
tipos_coluna = ["texto", "numero", "data", "link", "booleano"]
```

### **Configurar Filtros Padrão**
```python
filtros_padrao = ["ano", "tema", "orgao", "tipo"]
```

## 🔮 Próximas Funcionalidades

- [ ] **Gráficos automáticos** das tabelas
- [ ] **Integração com Power BI**
- [ ] **Templates pré-definidos**
- [ ] **Análise estatística automática**
- [ ] **Exportação para Google Sheets**
- [ ] **Agendamento de relatórios**

## 🏆 Status

**✅ SISTEMA FUNCIONAL E PRONTO PARA USO**

- ✅ IA direcionada implementada
- ✅ Interface CLI funcional
- ✅ Interface web moderna
- ✅ Múltiplos formatos de saída
- ✅ Documentação completa
- ✅ Testes básicos incluídos

---

**🌱 Desenvolvido para organizar eficientemente as leis ambientais do Tocantins** 📊🚀