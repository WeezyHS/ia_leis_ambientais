# 📋 PLANO DE INCLUSÃO DE FONTES FEDERAIS
## Decreto de Implementação Futura

### 🎯 OBJETIVO
Incluir as principais fontes de legislação ambiental federal que estão ausentes no sistema atual.

---

## 🏛️ FONTES FEDERAIS A IMPLEMENTAR

### 1. **Planalto.gov.br**
- **Tipo**: Leis Federais, Decretos, Medidas Provisórias
- **Importância**: ⭐⭐⭐⭐⭐ (Crítica)
- **Conteúdo**: 
  - Lei 6938/1981 (Política Nacional do Meio Ambiente)
  - Lei 9605/1998 (Lei de Crimes Ambientais)
  - Lei 12651/2012 (Código Florestal)
  - Lei 9985/2000 (SNUC)
  - Lei 12305/2010 (Política Nacional de Resíduos Sólidos)
  - Lei 11428/2006 (Lei da Mata Atlântica)
- **Status**: ❌ NÃO IMPLEMENTADO

### 2. **CONAMA (Conselho Nacional do Meio Ambiente)**
- **Tipo**: Resoluções CONAMA
- **Importância**: ⭐⭐⭐⭐⭐ (Crítica)
- **Conteúdo**:
  - Resolução 237/1997 (Licenciamento Ambiental)
  - Resolução 357/2005 (Qualidade das Águas)
  - Resolução 430/2011 (Condições de Lançamento)
  - Resolução 001/1986 (EIA/RIMA)
  - Resolução 303/2002 (APPs)
- **Status**: ❌ NÃO IMPLEMENTADO

### 3. **IBAMA / CTF / TCFA**
- **Tipo**: Instruções Normativas, Portarias
- **Importância**: ⭐⭐⭐⭐ (Alta)
- **Conteúdo**:
  - Instruções Normativas do IBAMA
  - Normas do Cadastro Técnico Federal
  - Normas sobre TCFA (Taxa de Controle e Fiscalização Ambiental)
- **Status**: ❌ NÃO IMPLEMENTADO

---

## ✅ FONTES JÁ IMPLEMENTADAS

### **Estadual (TO)**
- ✅ **Naturatins / SIGAM**: Implementado
- ✅ **COEMA/TO**: Implementado  
- ✅ **Secretaria Estadual do Meio Ambiente**: Implementado

### **Municipal**
- ❌ **Site da prefeitura**: NÃO IMPLEMENTADO
- ❌ **Plano Diretor e Código Ambiental**: NÃO IMPLEMENTADO

### **Técnicas**
- ✅ **ABNT**: Implementado (18 normas)

---

## 🚀 ESTRATÉGIA DE IMPLEMENTAÇÃO

### **FASE 1: Fontes Federais Críticas**
1. **Planalto.gov.br**
   - Implementar scraper para leis federais
   - Focar nas 6 leis ambientais principais
   - Criar parser para estrutura HTML do Planalto

2. **CONAMA**
   - Implementar scraper para resoluções
   - Focar nas 10 resoluções mais importantes
   - Criar parser específico para formato CONAMA

### **FASE 2: Órgãos Federais**
3. **IBAMA**
   - Implementar scraper para Instruções Normativas
   - Focar em normas de licenciamento e fiscalização
   - Integrar com sistema de CTF/TCFA

### **FASE 3: Fontes Municipais**
4. **Prefeituras**
   - Implementar scrapers genéricos para sites municipais
   - Focar em Planos Diretores e Códigos Ambientais
   - Criar sistema adaptável para diferentes municípios

---

## 🛠️ ARQUIVOS A CRIAR/MODIFICAR

### **Novos Scrapers**
- `app/services/planalto_scraper.py`
- `app/services/conama_scraper.py`
- `app/services/ibama_scraper.py`
- `app/services/municipal_scraper.py`

### **Modificações**
- `app/services/multi_source_scraper.py` (adicionar novos scrapers)
- `tabela_generator/ia_tabela_service.py` (incluir novas fontes)
- `tabela_generator/web_interface.py` (atualizar interface)

### **Novos Arquivos de Dados**
- `leis_federais_planalto.json`
- `resolucoes_conama.json`
- `normas_ibama.json`
- `leis_municipais.json`

---

## 📊 IMPACTO ESPERADO

### **Antes (Situação Atual)**
- 289 documentos total
- Apenas legislação estadual (TO) + ABNT
- ❌ Sem leis federais fundamentais
- ❌ Sem resoluções CONAMA

### **Depois (Pós-Implementação)**
- ~500-800 documentos estimados
- ✅ Legislação completa: Federal + Estadual + Municipal
- ✅ Todas as leis federais ambientais principais
- ✅ Principais resoluções CONAMA
- ✅ Normas técnicas IBAMA

---

## ⚠️ CONSIDERAÇÕES TÉCNICAS

### **Desafios Identificados**
1. **Rate Limiting**: Sites governamentais podem ter limitações
2. **Estrutura HTML**: Cada site tem formato diferente
3. **Atualizações**: Leis podem ser alteradas/revogadas
4. **Volume**: Aumento significativo de dados no Pinecone

### **Soluções Propostas**
1. **Cache Inteligente**: Sistema de cache com TTL
2. **Parsers Robustos**: Múltiplas estratégias de extração
3. **Versionamento**: Controle de versões das leis
4. **Otimização**: Chunking inteligente para Pinecone

---

## 📅 CRONOGRAMA SUGERIDO

### **Semana 1-2: Planalto.gov.br**
- Implementar scraper básico
- Indexar 6 leis federais principais
- Testes e validação

### **Semana 3-4: CONAMA**
- Implementar scraper CONAMA
- Indexar 10 resoluções principais
- Integração com sistema existente

### **Semana 5-6: IBAMA**
- Implementar scraper IBAMA
- Indexar Instruções Normativas
- Testes de performance

### **Semana 7-8: Municipal**
- Implementar scrapers municipais
- Piloto com 2-3 municípios
- Documentação final

---

## 🎯 DECRETO FINAL

**FICA DECRETADO** que o sistema de IA para Leis Ambientais será expandido para incluir:

1. ✅ **TODAS** as principais leis federais ambientais via Planalto.gov.br
2. ✅ **TODAS** as principais resoluções CONAMA
3. ✅ **PRINCIPAIS** normas do IBAMA/CTF/TCFA
4. ✅ **PILOTO** para legislação municipal

**Objetivo**: Transformar o sistema de uma base **estadual** para uma base **nacional completa** de legislação ambiental.

**Status**: 📋 **PLANEJADO** - Aguardando execução

---

*Documento criado em: 08/01/2025*  
*Última atualização: 08/01/2025*