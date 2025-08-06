"""
Verificador de Status do Pinecone - Analisa se há dados duplicados
Verifica o estado atual do índice e identifica possíveis duplicações
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from collections import defaultdict

load_dotenv()

class PineconeStatusChecker:
    """Verifica o status e possíveis duplicações no Pinecone"""
    
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "leis-ambientais")
        self.index = self.pc.Index(self.index_name)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    def get_index_stats(self) -> dict:
        """Obtém estatísticas do índice"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "namespaces": stats.namespaces,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def sample_vectors_by_namespace(self, namespace: str = "", limit: int = 100) -> list:
        """Obtém uma amostra de vetores de um namespace"""
        try:
            # Faz uma busca com vetor aleatório para obter amostras
            dummy_vector = [0.1] * 1536  # Dimensão do text-embedding-3-small
            
            response = self.index.query(
                vector=dummy_vector,
                top_k=limit,
                namespace=namespace,
                include_metadata=True
            )
            
            return response.matches
        except Exception as e:
            print(f"❌ Erro ao obter amostras do namespace '{namespace}': {e}")
            return []
    
    def analyze_duplicates(self, vectors: list) -> dict:
        """Analisa possíveis duplicações nos vetores"""
        analysis = {
            "total_vectors": len(vectors),
            "unique_titles": set(),
            "title_counts": defaultdict(int),
            "id_patterns": defaultdict(int),
            "potential_duplicates": [],
            "chunk_analysis": defaultdict(list)
        }
        
        for vector in vectors:
            metadata = vector.metadata
            vector_id = vector.id
            
            # Analisa títulos
            titulo = metadata.get('titulo', 'Sem título')
            analysis["unique_titles"].add(titulo)
            analysis["title_counts"][titulo] += 1
            
            # Analisa padrões de ID
            if 'lei_' in vector_id and '_chunk_' in vector_id:
                lei_part = vector_id.split('_chunk_')[0]
                analysis["id_patterns"][lei_part] += 1
                analysis["chunk_analysis"][lei_part].append({
                    "id": vector_id,
                    "chunk_index": metadata.get('chunk_index', 0),
                    "titulo": titulo
                })
            
            # Identifica possíveis duplicatas por título
            if analysis["title_counts"][titulo] > 10:  # Muitos chunks do mesmo título
                analysis["potential_duplicates"].append({
                    "titulo": titulo,
                    "count": analysis["title_counts"][titulo],
                    "id": vector_id
                })
        
        return analysis
    
    def check_for_duplicates(self) -> dict:
        """Verifica duplicações em todos os namespaces"""
        print("🔍 VERIFICANDO DUPLICAÇÕES NO PINECONE...")
        
        stats = self.get_index_stats()
        if not stats:
            return {"erro": "Não foi possível obter estatísticas"}
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"  Total de vetores: {stats.get('total_vectors', 0):,}")
        print(f"  Dimensão: {stats.get('dimension', 0)}")
        print(f"  Ocupação do índice: {stats.get('index_fullness', 0):.2%}")
        
        namespaces = stats.get('namespaces', {})
        print(f"  Namespaces: {len(namespaces)}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "namespace_analysis": {}
        }
        
        # Analisa cada namespace
        for namespace_name, namespace_stats in namespaces.items():
            namespace_display = namespace_name if namespace_name else "default"
            vector_count = namespace_stats.get('vector_count', 0)
            
            print(f"\n🔍 Analisando namespace '{namespace_display}' ({vector_count:,} vetores)...")
            
            # Obtém amostra de vetores
            sample_vectors = self.sample_vectors_by_namespace(namespace_name, min(vector_count, 200))
            
            if sample_vectors:
                # Analisa duplicações
                analysis = self.analyze_duplicates(sample_vectors)
                
                print(f"  📄 Amostra analisada: {analysis['total_vectors']} vetores")
                print(f"  📚 Títulos únicos: {len(analysis['unique_titles'])}")
                print(f"  🔢 Padrões de ID únicos: {len(analysis['id_patterns'])}")
                
                # Verifica se há muitas duplicações
                high_count_titles = [titulo for titulo, count in analysis['title_counts'].items() if count > 15]
                if high_count_titles:
                    print(f"  ⚠️ Títulos com muitos chunks: {len(high_count_titles)}")
                    for titulo in high_count_titles[:3]:  # Mostra apenas os primeiros 3
                        count = analysis['title_counts'][titulo]
                        print(f"    - {titulo}: {count} chunks")
                else:
                    print(f"  ✅ Nenhuma duplicação excessiva detectada")
                
                results["namespace_analysis"][namespace_display] = {
                    "vector_count": vector_count,
                    "sample_size": len(sample_vectors),
                    "unique_titles": len(analysis['unique_titles']),
                    "id_patterns": len(analysis['id_patterns']),
                    "high_count_titles": len(high_count_titles),
                    "title_counts": dict(analysis['title_counts']),
                    "chunk_analysis": dict(analysis['chunk_analysis'])
                }
            else:
                print(f"  ❌ Não foi possível obter amostras")
                results["namespace_analysis"][namespace_display] = {
                    "error": "Não foi possível obter amostras"
                }
        
        return results
    
    def search_for_specific_content(self, query: str, namespace: str = "") -> list:
        """Busca por conteúdo específico para verificar duplicações"""
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            response = self.index.query(
                vector=query_embedding,
                top_k=20,
                namespace=namespace,
                include_metadata=True
            )
            
            return response.matches
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def test_duplicate_search(self) -> dict:
        """Testa busca por possíveis duplicações"""
        print("\n🔍 TESTANDO BUSCA POR DUPLICAÇÕES...")
        
        test_queries = [
            "Lei nº 1307 de 2002",
            "recursos hídricos",
            "licenciamento ambiental",
            "política estadual"
        ]
        
        results = {}
        
        for query in test_queries:
            print(f"\n  Buscando: '{query}'")
            
            # Busca no namespace padrão
            matches = self.search_for_specific_content(query, "")
            
            if matches:
                print(f"    Encontrados: {len(matches)} resultados")
                
                # Analisa se há duplicações
                titles = [match.metadata.get('titulo', 'Sem título') for match in matches]
                unique_titles = set(titles)
                
                print(f"    Títulos únicos: {len(unique_titles)}")
                
                if len(titles) > len(unique_titles) * 2:  # Muitos resultados para poucos títulos
                    print(f"    ⚠️ Possível duplicação detectada")
                else:
                    print(f"    ✅ Distribuição normal")
                
                results[query] = {
                    "total_matches": len(matches),
                    "unique_titles": len(unique_titles),
                    "titles": list(unique_titles)[:5]  # Primeiros 5 títulos
                }
            else:
                print(f"    Nenhum resultado encontrado")
                results[query] = {"total_matches": 0}
        
        return results
    
    def generate_report(self, analysis: dict, search_test: dict) -> str:
        """Gera relatório sobre duplicações"""
        report = f"""
=== RELATÓRIO DE VERIFICAÇÃO DO PINECONE ===

📊 ESTATÍSTICAS GERAIS:
  • Total de vetores: {analysis['stats'].get('total_vectors', 0):,}
  • Namespaces: {len(analysis['stats'].get('namespaces', {})):,}
  • Ocupação do índice: {analysis['stats'].get('index_fullness', 0):.2%}

🔍 ANÁLISE POR NAMESPACE:
"""
        
        for namespace, data in analysis.get('namespace_analysis', {}).items():
            if 'error' in data:
                report += f"  • {namespace}: Erro na análise\n"
                continue
            
            vector_count = data.get('vector_count', 0)
            unique_titles = data.get('unique_titles', 0)
            high_count = data.get('high_count_titles', 0)
            
            report += f"  • {namespace}: {vector_count:,} vetores, {unique_titles} títulos únicos\n"
            
            if high_count > 0:
                report += f"    ⚠️ {high_count} títulos com muitos chunks (possível duplicação)\n"
            else:
                report += f"    ✅ Distribuição normal de chunks\n"
        
        report += f"\n🔍 TESTE DE BUSCA POR DUPLICAÇÕES:\n"
        
        for query, result in search_test.items():
            total = result.get('total_matches', 0)
            unique = result.get('unique_titles', 0)
            
            if total > 0:
                ratio = total / max(unique, 1)
                status = "⚠️ Possível duplicação" if ratio > 3 else "✅ Normal"
                report += f"  • '{query}': {total} resultados, {unique} títulos únicos - {status}\n"
            else:
                report += f"  • '{query}': Nenhum resultado\n"
        
        # Conclusão
        total_vectors = analysis['stats'].get('total_vectors', 0)
        if total_vectors > 200:
            report += f"\n⚠️ ATENÇÃO: Índice com {total_vectors:,} vetores pode indicar duplicação.\n"
            report += f"Para 21 leis expandidas, esperamos ~100-150 vetores.\n"
        else:
            report += f"\n✅ CONCLUSÃO: Quantidade de vetores parece normal para o conteúdo.\n"
        
        return report

def main():
    """Função principal"""
    print("=== VERIFICAÇÃO DE STATUS DO PINECONE ===")
    print("Este script irá:")
    print("1. Verificar estatísticas do índice")
    print("2. Analisar possíveis duplicações")
    print("3. Testar busca por conteúdo duplicado")
    print("4. Gerar relatório de status")
    
    try:
        checker = PineconeStatusChecker()
        
        # Verifica duplicações
        analysis = checker.check_for_duplicates()
        
        # Testa busca por duplicações
        search_test = checker.test_duplicate_search()
        
        # Gera relatório
        report = checker.generate_report(analysis, search_test)
        print(report)
        
        # Salva resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"tests/pinecone_status_{timestamp}.json"
        
        full_results = {
            "analysis": analysis,
            "search_test": search_test,
            "report": report
        }
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(full_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 Resultados salvos em: {results_file}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()