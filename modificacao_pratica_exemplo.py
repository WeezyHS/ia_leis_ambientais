#!/usr/bin/env python3
"""
EXEMPLO PRÁTICO: Como você usaria APIs do governo federal

Este é um exemplo REAL de como modificar a função _legislacoes_federais
para buscar a "Descrição Resumida" de APIs do governo.
"""

def exemplo_antes_e_depois():
    """Mostra a diferença entre ANTES e DEPOIS da modificação"""
    
    print("🔴 ANTES (Problema atual):")
    print("=" * 50)
    
    # VERSÃO ATUAL - Dados pré-definidos
    def _legislacoes_federais_ATUAL(grupo_atividade, limite=10):
        """Versão atual com textos pré-definidos"""
        
        legislacoes_predefinidas = {
            "Agricultura": [
                {
                    "esfera": "Federal",
                    "titulo_legislacao": "Lei nº 12.651, de 25 de maio de 2012 (Código Florestal Brasileiro)",
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": "Texto genérico pré-definido sobre código florestal",  # ❌ PROBLEMA
                    "aplicabilidade": "Texto genérico sobre aplicabilidade"  # ❌ PROBLEMA
                }
            ]
        }
        
        return legislacoes_predefinidas.get(grupo_atividade, [])[:limite]
    
    # Executar versão atual
    leis_atuais = _legislacoes_federais_ATUAL("Agricultura", 1)
    for lei in leis_atuais:
        print(f"📄 {lei['titulo_legislacao']}")
        print(f"📝 Descrição: {lei['descricao_resumida']}")
        print(f"🎯 Aplicabilidade: {lei['aplicabilidade']}")
    
    print("\n" + "="*50)
    print("🟢 DEPOIS (Com APIs do governo):")
    print("=" * 50)
    
    # NOVA VERSÃO - Com APIs do governo
    def _legislacoes_federais_NOVA(grupo_atividade, limite=10):
        """Nova versão que busca dados REAIS das APIs"""
        
        import requests
        
        # 1️⃣ BUSCAR DADOS REAIS DA API
        try:
            # Exemplo: Buscar Lei 12651/2012 (Código Florestal)
            dados_api = buscar_lei_api_governo("12651", "2012")
            
            if dados_api:
                return [{
                    "esfera": "Federal",
                    "titulo_legislacao": dados_api["titulo_oficial"],
                    "vigencia": "✅ Vigente",
                    "descricao_resumida": dados_api["ementa_real"],  # ✅ DADOS REAIS
                    "aplicabilidade": dados_api["aplicabilidade_real"],  # ✅ DADOS REAIS
                    "fonte": "API Governo Federal",
                    "url_oficial": dados_api["url"]
                }]
        
        except Exception as e:
            print(f"⚠️ Erro na API: {e}")
        
        # 2️⃣ FALLBACK: Dados pré-definidos apenas se API falhar
        return _legislacoes_federais_ATUAL(grupo_atividade, limite)
    
    def buscar_lei_api_governo(numero_lei, ano):
        """Simula busca na API do governo"""
        
        # EXEMPLO REAL: Como seria a resposta da API
        apis_disponiveis = {
            "12651_2012": {
                "titulo_oficial": "Lei nº 12.651, de 25 de maio de 2012",
                "ementa_real": "Dispõe sobre a proteção da vegetação nativa; altera as Leis nºs 6.938, de 31 de agosto de 1981, 9.393, de 19 de dezembro de 1996, e 11.428, de 22 de dezembro de 2006; revoga as Leis nºs 4.771, de 15 de setembro de 1965, e 7.754, de 14 de abril de 1989, e a Medida Provisória nº 2.166-67, de 24 de agosto de 2001; e dá outras providências.",
                "aplicabilidade_real": "Aplicável a todas as propriedades rurais do território nacional. No Tocantins (Cerrado), exige Reserva Legal mínima de 35% da área total da propriedade, podendo ser reduzida para 20% mediante compensação em outra área.",
                "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12651.htm",
                "orgao_responsavel": "Ministério do Meio Ambiente",
                "status": "vigente"
            }
        }
        
        chave = f"{numero_lei}_{ano}"
        return apis_disponiveis.get(chave)
    
    # Executar nova versão
    leis_novas = _legislacoes_federais_NOVA("Agricultura", 1)
    for lei in leis_novas:
        print(f"📄 {lei['titulo_legislacao']}")
        print(f"📝 Descrição: {lei['descricao_resumida']}")
        print(f"🎯 Aplicabilidade: {lei['aplicabilidade']}")
        print(f"🌐 Fonte: {lei.get('fonte', 'Dados pré-definidos')}")

def exemplo_apis_especificas():
    """Mostra quais APIs específicas você usaria"""
    
    print("\n🌐 APIS ESPECÍFICAS QUE VOCÊ USARIA:")
    print("=" * 50)
    
    apis_governo = {
        "Portal de Dados Abertos": {
            "url": "https://dados.gov.br/api/publico/conjuntos-dados",
            "uso": "Buscar datasets de legislação ambiental",
            "exemplo": "?q=lei+12651+codigo+florestal&organization=ministerio-do-meio-ambiente"
        },
        
        "Planalto (Scraping Estruturado)": {
            "url": "https://www.planalto.gov.br/ccivil_03",
            "uso": "Acessar texto oficial das leis",
            "exemplo": "/leis/l12651.htm"
        },
        
        "IBAMA API": {
            "url": "https://servicos.ibama.gov.br/api",
            "uso": "Dados de fiscalização e normas",
            "exemplo": "/normas/resolucoes"
        },
        
        "Base dos Dados": {
            "url": "https://basedosdados.org/dataset/br-gov-legislacao-ambiental",
            "uso": "Dados tratados de legislação",
            "exemplo": "API GraphQL para consultas estruturadas"
        }
    }
    
    for nome, info in apis_governo.items():
        print(f"\n📡 {nome}")
        print(f"   🔗 URL: {info['url']}")
        print(f"   💡 Uso: {info['uso']}")
        print(f"   📋 Exemplo: {info['exemplo']}")

def exemplo_fluxo_completo():
    """Mostra o fluxo completo de como funcionaria"""
    
    print("\n🔄 FLUXO COMPLETO DA INTEGRAÇÃO:")
    print("=" * 50)
    
    fluxo = [
        "1️⃣ Usuário solicita tabela para 'Agricultura'",
        "2️⃣ Sistema identifica leis federais relevantes (12651, 6938, 9605, etc.)",
        "3️⃣ Para cada lei, tenta buscar na API do governo:",
        "   📡 Portal de Dados Abertos → Busca dataset da lei",
        "   📄 Planalto → Extrai ementa oficial",
        "   🏛️ IBAMA → Verifica normas complementares",
        "4️⃣ Se encontrar dados reais:",
        "   ✅ Usa ementa oficial como 'Descrição Resumida'",
        "   ✅ Gera aplicabilidade baseada no texto real",
        "5️⃣ Se API falhar:",
        "   🔄 Usa dados pré-definidos como fallback",
        "6️⃣ Retorna tabela com dados REAIS + fallback quando necessário"
    ]
    
    for passo in fluxo:
        print(passo)

def exemplo_resultado_final():
    """Mostra como seria o resultado final"""
    
    print("\n📊 RESULTADO FINAL - COMPARAÇÃO:")
    print("=" * 50)
    
    print("🔴 ANTES (Texto pré-definido):")
    print("Descrição: 'Texto genérico sobre código florestal'")
    
    print("\n🟢 DEPOIS (Dados reais da API):")
    print("Descrição: 'Dispõe sobre a proteção da vegetação nativa; altera as Leis nºs 6.938, de 31 de agosto de 1981, 9.393, de 19 de dezembro de 1996, e 11.428, de 22 de dezembro de 2006; revoga as Leis nºs 4.771, de 15 de setembro de 1965, e 7.754, de 14 de abril de 1989, e a Medida Provisória nº 2.166-67, de 24 de agosto de 2001; e dá outras providências.'")
    
    print("\n💡 VANTAGENS:")
    vantagens = [
        "✅ Descrições oficiais e precisas",
        "✅ Sempre atualizadas",
        "✅ Maior credibilidade",
        "✅ Informações completas",
        "✅ Rastreabilidade da fonte"
    ]
    
    for vantagem in vantagens:
        print(f"   {vantagem}")

if __name__ == "__main__":
    exemplo_antes_e_depois()
    exemplo_apis_especificas()
    exemplo_fluxo_completo()
    exemplo_resultado_final()