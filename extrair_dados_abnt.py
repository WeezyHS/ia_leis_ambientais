#!/usr/bin/env python3
"""
Script para extrair dados da ABNT do Pinecone ou criar dados de exemplo
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório app ao path
sys.path.append(str(Path(__file__).parent / "app"))

def criar_dados_exemplo_abnt():
    """Cria dados de exemplo da ABNT baseados em normas ambientais conhecidas"""
    
    normas_exemplo = [
        {
            "source": "ABNT",
            "codigo": "ABNT NBR ISO 14001:2015",
            "titulo": "Sistemas de gestão ambiental - Requisitos com orientações para uso",
            "status": "Vigente",
            "text": "Esta Norma especifica os requisitos para um sistema de gestão ambiental que uma organização pode usar para desenvolver seu desempenho ambiental. Esta Norma é destinada ao uso por uma organização que busca gerenciar suas responsabilidades ambientais de forma sistemática, que contribua para o pilar ambiental da sustentabilidade.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Sistema de gestão ambiental - Requisitos e orientações",
            "escopo": "Gestão Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Sistema de Gestão",
            "preco": "BRL 108,00",
            "ano": "2015"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR ISO 14040:2025",
            "titulo": "Gestão ambiental - Avaliação do ciclo de vida - Princípios e estrutura",
            "status": "Vigente",
            "text": "Esta Norma especifica princípios e estrutura para avaliação do ciclo de vida (ACV), incluindo: definição do objetivo e escopo da ACV, fase de análise do inventário do ciclo de vida (ICV), fase de avaliação do impacto do ciclo de vida (AICV), fase de interpretação do ciclo de vida, relatório e análise crítica da ACV, limitações da ACV, relação entre as fases da ACV, e condições para uso de escolhas de valores e elementos opcionais.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Avaliação do ciclo de vida - Princípios e estrutura",
            "escopo": "Avaliação Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Avaliação de Impacto",
            "preco": "BRL 95,00",
            "ano": "2025"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR ISO 14030-3:2025",
            "titulo": "Avaliação de desempenho ambiental - Parte 3: Diretrizes para organizações",
            "status": "Vigente",
            "text": "Esta parte da ABNT NBR ISO 14030 fornece diretrizes para organizações sobre como conduzir avaliações de desempenho ambiental. Inclui orientações sobre estabelecimento de indicadores de desempenho ambiental, coleta e análise de dados, e comunicação de resultados.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Avaliação de desempenho ambiental para organizações",
            "escopo": "Desempenho Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Avaliação de Desempenho",
            "preco": "BRL 87,00",
            "ano": "2025"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT PR 2030-1:2024",
            "titulo": "Ambiental, social e governança (ESG) - Parte 1: Terminologia e conceitos",
            "status": "Vigente",
            "text": "Este projeto de norma estabelece terminologia e conceitos relacionados a critérios ambientais, sociais e de governança (ESG). Define termos fundamentais para implementação de práticas ESG em organizações.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Critérios ESG - Terminologia e conceitos",
            "escopo": "ESG",
            "comite": "ABNT/CB-038",
            "categoria": "Sustentabilidade",
            "preco": "BRL 72,00",
            "ano": "2024"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 9895:2025",
            "titulo": "Passivo ambiental em solo e água subterrânea",
            "status": "Vigente",
            "text": "Esta Norma estabelece procedimentos para identificação, avaliação e gerenciamento de passivos ambientais em solo e água subterrânea. Inclui metodologias para investigação, análise de risco e proposição de medidas de remediação.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Procedimentos para passivos ambientais em solo e água",
            "escopo": "Remediação Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Passivo Ambiental",
            "preco": "BRL 156,00",
            "ano": "2025"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR ISO 14064-1:2007",
            "titulo": "Gases de efeito estufa - Parte 1: Especificação e orientações para quantificação e elaboração de relatórios de emissões e remoções de gases de efeito estufa no nível da organização",
            "status": "Vigente",
            "text": "Esta parte da ABNT NBR ISO 14064 especifica princípios e requisitos para o projeto, desenvolvimento, gerenciamento, elaboração de relatórios e verificação de inventários de gases de efeito estufa (GEE) de organizações ou empresas.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Quantificação de gases de efeito estufa - Organizações",
            "escopo": "Mudanças Climáticas",
            "comite": "ABNT/CB-038",
            "categoria": "Gases de Efeito Estufa",
            "preco": "BRL 124,00",
            "ano": "2007"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR ISO 14046:2014",
            "titulo": "Gestão ambiental - Pegada hídrica - Princípios, requisitos e diretrizes",
            "status": "Vigente",
            "text": "Esta Norma especifica princípios, requisitos e diretrizes relacionados à avaliação da pegada hídrica de produtos, processos e organizações com base na avaliação do ciclo de vida (ACV).",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Avaliação da pegada hídrica",
            "escopo": "Recursos Hídricos",
            "comite": "ABNT/CB-038",
            "categoria": "Pegada Hídrica",
            "preco": "BRL 98,00",
            "ano": "2014"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 10004:2004",
            "titulo": "Resíduos sólidos - Classificação",
            "status": "Vigente",
            "text": "Esta Norma classifica os resíduos sólidos quanto aos seus riscos potenciais ao meio ambiente e à saúde pública, para que possam ser gerenciados adequadamente.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Classificação de resíduos sólidos",
            "escopo": "Gestão de Resíduos",
            "comite": "ABNT/CB-038",
            "categoria": "Resíduos Sólidos",
            "preco": "BRL 89,00",
            "ano": "2004"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 13896:1997",
            "titulo": "Aterros de resíduos não perigosos - Critérios para projeto, implantação e operação",
            "status": "Vigente",
            "text": "Esta Norma fixa as condições exigíveis para projeto, implantação e operação de aterros de resíduos não perigosos, de forma a proteger adequadamente as coleções hídricas superficiais e subterrâneas próximas, bem como os operadores destas instalações e populações vizinhas.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Critérios para aterros de resíduos não perigosos",
            "escopo": "Aterros Sanitários",
            "comite": "ABNT/CB-038",
            "categoria": "Disposição de Resíduos",
            "preco": "BRL 76,00",
            "ano": "1997"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 15495-1:2007",
            "titulo": "Poços de monitoramento de águas subterrâneas em aquíferos granulares - Parte 1: Projeto e construção",
            "status": "Vigente",
            "text": "Esta parte da ABNT NBR 15495 estabelece os requisitos para projeto e construção de poços de monitoramento de águas subterrâneas em aquíferos granulares.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Poços de monitoramento - Projeto e construção",
            "escopo": "Monitoramento Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Águas Subterrâneas",
            "preco": "BRL 67,00",
            "ano": "2007"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 16209:2013",
            "titulo": "Avaliação de risco à saúde humana para fins de gerenciamento de áreas contaminadas",
            "status": "Vigente",
            "text": "Esta Norma estabelece os procedimentos para avaliação de risco à saúde humana decorrente da exposição a substâncias químicas em áreas contaminadas.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Avaliação de risco em áreas contaminadas",
            "escopo": "Áreas Contaminadas",
            "comite": "ABNT/CB-038",
            "categoria": "Avaliação de Risco",
            "preco": "BRL 134,00",
            "ano": "2013"
        },
        {
            "source": "ABNT",
            "codigo": "ABNT NBR 15515-1:2007",
            "titulo": "Passivo ambiental em solo e água subterrânea - Parte 1: Avaliação preliminar",
            "status": "Vigente",
            "text": "Esta parte da ABNT NBR 15515 estabelece procedimentos para condução de avaliação preliminar em áreas com potencial de contaminação ou suspeitas de contaminação.",
            "type": "norma_abnt",
            "collected_at": datetime.now().isoformat(),
            "resumo": "Avaliação preliminar de passivos ambientais",
            "escopo": "Investigação Ambiental",
            "comite": "ABNT/CB-038",
            "categoria": "Passivo Ambiental",
            "preco": "BRL 89,00",
            "ano": "2007"
        }
    ]
    
    return normas_exemplo

def tentar_extrair_pinecone():
    """Tenta extrair dados da ABNT do Pinecone"""
    try:
        from services.pinecone_service import pinecone_index
        
        print("🔍 Tentando acessar dados da ABNT no Pinecone...")
        
        # Obter estatísticas dos namespaces
        stats = pinecone_index.describe_index_stats()
        
        if "abnt-normas" in stats.namespaces:
            abnt_count = stats.namespaces["abnt-normas"].vector_count
            print(f"📊 Encontradas {abnt_count} normas ABNT no Pinecone")
            
            # Fazer uma consulta para obter dados reais
            response = pinecone_index.query(
                vector=[0.0] * 1536,  # Vector dummy para busca
                top_k=min(abnt_count, 50),  # Máximo 50 normas
                namespace="abnt-normas",
                include_metadata=True
            )
            
            normas_pinecone = []
            for match in response.matches:
                metadata = match.metadata
                norma = {
                    "source": "ABNT",
                    "codigo": metadata.get("codigo", "N/A"),
                    "titulo": metadata.get("titulo", metadata.get("title", "N/A")),
                    "status": metadata.get("status", "Vigente"),
                    "text": metadata.get("text", metadata.get("content", "")),
                    "type": "norma_abnt",
                    "collected_at": metadata.get("collected_at", datetime.now().isoformat()),
                    "resumo": metadata.get("resumo", ""),
                    "escopo": metadata.get("escopo", ""),
                    "comite": metadata.get("comite", ""),
                    "categoria": metadata.get("categoria", "Norma Técnica"),
                    "preco": metadata.get("preco", ""),
                    "ano": metadata.get("ano", "")
                }
                normas_pinecone.append(norma)
            
            return normas_pinecone
            
        else:
            print("⚠️ Namespace 'abnt-normas' não encontrado no Pinecone")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao acessar Pinecone: {e}")
        return None

def main():
    """Função principal"""
    
    print("🔧 Extraindo dados da ABNT...")
    print("=" * 50)
    
    # Tentar extrair do Pinecone primeiro
    normas = tentar_extrair_pinecone()
    
    if not normas:
        print("💡 Usando dados de exemplo da ABNT...")
        normas = criar_dados_exemplo_abnt()
    
    if normas:
        # Salvar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"abnt_normas_ambientais_{timestamp}.json"
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(normas, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Extração concluída!")
        print(f"📄 {len(normas)} normas extraídas")
        print(f"💾 Dados salvos em: {arquivo_saida}")
        
        # Mostrar estatísticas
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Total de normas: {len(normas)}")
        
        # Contar por categoria
        categorias = {}
        for norma in normas:
            cat = norma.get('categoria', 'N/A')
            categorias[cat] = categorias.get(cat, 0) + 1
        
        for categoria, count in categorias.items():
            print(f"   • {categoria}: {count}")
        
        # Mostrar exemplos
        print(f"\n📋 EXEMPLOS DE NORMAS:")
        for i, norma in enumerate(normas[:5]):
            codigo = norma.get('codigo', 'N/A')
            titulo = norma.get('titulo', 'N/A')[:60] + "..." if len(norma.get('titulo', '')) > 60 else norma.get('titulo', 'N/A')
            print(f"   {i+1}. {codigo} - {titulo}")
        
        if len(normas) > 5:
            print(f"   ... e mais {len(normas) - 5} normas")
            
        return arquivo_saida
        
    else:
        print("❌ Não foi possível extrair dados da ABNT")
        return None

if __name__ == "__main__":
    main()