#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de linha de comando para o gerador de tabelas de leis ambientais
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path para importar o módulo
sys.path.append(str(Path(__file__).parent.parent))

from tabela_generator.ia_tabela_service import IATabela
import json

class InterfaceTabela:
    """Interface para interação com o gerador de tabelas"""
    
    def __init__(self):
        """Inicializa a interface"""
        try:
            self.ia_tabela = IATabela()
            print("✅ IA Tabela inicializada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar IA Tabela: {e}")
            sys.exit(1)
    
    def mostrar_menu(self):
        """Mostra o menu principal"""
        print("\n" + "="*60)
        print("🤖 IA DIRECIONADA - GERADOR DE TABELAS DE LEIS AMBIENTAIS")
        print("="*60)
        print("1. 📊 Gerar tabela vazia (estrutura apenas)")
        print("2. 📋 Gerar tabela com dados das leis")
        print("3. 🔍 Ver dados disponíveis")
        print("4. 📁 Listar tabelas salvas")
        print("5. ❌ Sair")
        print("="*60)
    
    def executar(self):
        """Executa o loop principal da interface"""
        while True:
            self.mostrar_menu()
            
            try:
                opcao = input("\n🎯 Escolha uma opção (1-5): ").strip()
                
                if opcao == "1":
                    self.gerar_tabela_vazia()
                elif opcao == "2":
                    self.gerar_tabela_com_dados()
                elif opcao == "3":
                    self.mostrar_dados_disponiveis()
                elif opcao == "4":
                    self.listar_tabelas_salvas()
                elif opcao == "5":
                    print("\n👋 Encerrando o gerador de tabelas...")
                    break
                else:
                    print("❌ Opção inválida! Escolha entre 1-5.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Encerrando o gerador de tabelas...")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
    
    def gerar_tabela_vazia(self):
        """Gera uma tabela vazia baseada na descrição do usuário"""
        print("\n📊 GERAÇÃO DE TABELA VAZIA")
        print("-" * 40)
        
        print("💡 Descreva como você quer organizar as leis ambientais na tabela.")
        print("   Exemplos:")
        print("   - 'Organizar por ano e tema principal'")
        print("   - 'Tabela com foco em licenciamento ambiental'")
        print("   - 'Agrupar leis por órgão responsável'")
        
        descricao = input("\n📝 Sua descrição: ").strip()
        
        if not descricao:
            print("❌ Descrição não pode estar vazia!")
            return
        
        print("\n🤖 Processando com IA direcionada...")
        
        try:
            # Gerar estrutura usando IA
            estrutura = self.ia_tabela.gerar_estrutura_tabela(descricao)
            
            print(f"\n✅ Estrutura gerada: {estrutura['titulo_tabela']}")
            print(f"📄 Descrição: {estrutura['descricao']}")
            
            # Gerar tabela vazia
            df_vazio = self.ia_tabela.gerar_tabela_vazia(estrutura)
            
            print(f"\n📊 TABELA VAZIA GERADA:")
            print("-" * 50)
            print(df_vazio.to_string(index=False))
            
            # Perguntar se quer salvar
            salvar = input("\n💾 Deseja salvar esta tabela? (s/N): ").strip().lower()
            
            if salvar in ['s', 'sim', 'y', 'yes']:
                formato = input("📁 Formato (excel/csv) [excel]: ").strip().lower()
                if not formato:
                    formato = "excel"
                
                caminho = self.ia_tabela.salvar_tabela(df_vazio, estrutura, formato)
                print(f"✅ Tabela salva em: {caminho}")
                
                # Gerar relatório
                relatorio = self.ia_tabela.gerar_relatorio_tabela(estrutura, df_vazio)
                caminho_relatorio = caminho.replace(f".{formato}", "_relatorio.md")
                
                with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                
                print(f"📋 Relatório salvo em: {caminho_relatorio}")
            
        except Exception as e:
            print(f"❌ Erro ao gerar tabela: {e}")
    
    def gerar_tabela_com_dados(self):
        """Gera uma tabela populada com dados das leis ou todas as fontes"""
        print("\n📋 GERAÇÃO DE TABELA COM DADOS")
        print("-" * 40)
        
        print("💡 Descreva como você quer organizar os dados ambientais na tabela.")
        descricao = input("\n📝 Sua descrição: ").strip()
        
        if not descricao:
            print("❌ Descrição não pode estar vazia!")
            return
        
        # Escolher fonte de dados
        print("\n📚 Escolha a fonte de dados:")
        print("1. 🏛️ Apenas Leis Estaduais do Tocantins (271 leis)")
        print("2. 🌐 TODAS as Fontes (Power BI, ABNT, COEMA, etc.)")
        
        try:
            opcao_fonte = input("Escolha (1/2) [2]: ").strip() or "2"
            incluir_todas_fontes = opcao_fonte == "2"
        except:
            incluir_todas_fontes = True
        
        if incluir_todas_fontes:
            total_disponivel = len(self.ia_tabela.todas_fontes_data)
            print(f"📊 Incluindo dados de TODAS as fontes ({total_disponivel} documentos disponíveis)")
            limite_padrao = 20
        else:
            total_disponivel = len(self.ia_tabela.leis_data)
            print(f"🏛️ Incluindo apenas leis estaduais do TO ({total_disponivel} leis disponíveis)")
            limite_padrao = 10
        
        try:
            limite = int(input(f"🔢 Quantos documentos incluir na tabela? [{limite_padrao}]: ").strip() or str(limite_padrao))
        except ValueError:
            limite = limite_padrao
        
        print(f"\n🤖 Processando {limite} documentos com IA direcionada...")
        
        try:
            # Gerar estrutura usando IA
            estrutura = self.ia_tabela.gerar_estrutura_tabela(descricao)
            
            print(f"\n✅ Estrutura gerada: {estrutura['titulo_tabela']}")
            
            # Gerar tabela com dados
            df_populado = self.ia_tabela.popular_tabela(estrutura, limite, incluir_todas_fontes)
            
            print(f"\n📊 TABELA COM DADOS GERADA:")
            print("-" * 50)
            print(df_populado.to_string(index=False))
            
            # Perguntar se quer salvar
            salvar = input("\n💾 Deseja salvar esta tabela? (s/N): ").strip().lower()
            
            if salvar in ['s', 'sim', 'y', 'yes']:
                formato = input("📁 Formato (excel/csv) [excel]: ").strip().lower()
                if not formato:
                    formato = "excel"
                
                caminho = self.ia_tabela.salvar_tabela(df_populado, estrutura, formato)
                print(f"✅ Tabela salva em: {caminho}")
                
                # Gerar relatório
                relatorio = self.ia_tabela.gerar_relatorio_tabela(estrutura, df_populado)
                caminho_relatorio = caminho.replace(f".{formato}", "_relatorio.md")
                
                with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                
                print(f"📋 Relatório salvo em: {caminho_relatorio}")
            
        except Exception as e:
            print(f"❌ Erro ao gerar tabela: {e}")
    
    def mostrar_dados_disponiveis(self):
        """Mostra informações sobre os dados disponíveis"""
        print("\n🔍 DADOS DISPONÍVEIS")
        print("-" * 40)
        
        total_leis = len(self.ia_tabela.leis_data)
        total_todas_fontes = len(self.ia_tabela.todas_fontes_data)
        
        print(f"🏛️ Leis Estaduais do Tocantins: {total_leis}")
        print(f"🌐 Total de TODAS as Fontes: {total_todas_fontes}")
        
        print("\n📚 FONTES DISPONÍVEIS:")
        print("   🏛️ Legislação Estadual TO (271 leis)")
        print("   📊 Power BI Dashboard (2.770 atos federais)")
        print("   🔧 ABNT (Normas técnicas)")
        print("   🌿 COEMA (Conselho Estadual)")
        print("   🇧🇷 CONAMA (Conselho Nacional)")
        print("   🛡️ IBAMA (Instruções normativas)")
        print("   🌳 ICMBio (Conservação)")
        
        if total_leis > 0:
            print("\n📋 Exemplo de lei estadual:")
            lei_exemplo = self.ia_tabela.leis_data[0]
            
            for campo, valor in lei_exemplo.items():
                valor_str = str(valor)[:100] + "..." if len(str(valor)) > 100 else str(valor)
                print(f"   • {campo}: {valor_str}")
        
        if total_todas_fontes > 0:
            print("\n📋 Exemplo de documento de todas as fontes:")
            doc_exemplo = self.ia_tabela.todas_fontes_data[0]
            
            for campo, valor in doc_exemplo.items():
                valor_str = str(valor)[:100] + "..." if len(str(valor)) > 100 else str(valor)
                print(f"   • {campo}: {valor_str}")
        
        print(f"\n💡 Campos disponíveis para organização:")
        print("   📊 TODAS AS FONTES:")
        print("      • fonte - Origem do documento")
        print("      • tipo - Tipo de documento")
        print("      • titulo - Título do documento")
        print("      • descricao - Descrição do documento")
        print("      • categoria - Categoria/classificação")
        print("      • jurisdicao - Abrangência (Federal/Estadual)")
        print("      • data_indexacao - Data de indexação")
        print("   🏛️ LEIS ESTADUAIS:")
        print("      • titulo - Título da lei")
        print("      • descricao - Descrição da lei")
        print("      • data - Data de publicação")
        print("      • link_arquivo - Link para o PDF")
        print("      • conteudo_parcial - Trecho do conteúdo")
    
    def listar_tabelas_salvas(self):
        """Lista as tabelas salvas no diretório"""
        print("\n📁 TABELAS SALVAS")
        print("-" * 40)
        
        diretorio = Path("c:/ia_leis_ambientais")
        tabelas_excel = list(diretorio.glob("tabela_*.xlsx"))
        tabelas_csv = list(diretorio.glob("tabela_*.csv"))
        relatorios = list(diretorio.glob("tabela_*_relatorio.md"))
        
        if not (tabelas_excel or tabelas_csv):
            print("📭 Nenhuma tabela salva encontrada.")
            return
        
        print("📊 Tabelas Excel:")
        for tabela in tabelas_excel:
            tamanho = tabela.stat().st_size / 1024  # KB
            print(f"   • {tabela.name} ({tamanho:.1f} KB)")
        
        print("\n📄 Tabelas CSV:")
        for tabela in tabelas_csv:
            tamanho = tabela.stat().st_size / 1024  # KB
            print(f"   • {tabela.name} ({tamanho:.1f} KB)")
        
        print("\n📋 Relatórios:")
        for relatorio in relatorios:
            tamanho = relatorio.stat().st_size / 1024  # KB
            print(f"   • {relatorio.name} ({tamanho:.1f} KB)")

def main():
    """Função principal"""
    interface = InterfaceTabela()
    interface.executar()

if __name__ == "__main__":
    main()