#!/usr/bin/env python3
"""
Gerador de PDF consolidado para normas ABNT ambientais
"""

import json
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class ABNTPDFGenerator:
    """Gerador de PDF para normas ABNT"""
    
    def __init__(self, arquivo_json: str):
        self.arquivo_json = arquivo_json
        self.dados = self._carregar_dados()
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
        
    def _carregar_dados(self) -> list:
        """Carrega dados do arquivo JSON"""
        try:
            with open(self.arquivo_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return []
    
    def _configurar_estilos(self):
        """Configura estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        ))
        
        # Título de seção
        self.styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Código da norma
        self.styles.add(ParagraphStyle(
            name='CodigoNorma',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        ))
        
        # Texto justificado
        self.styles.add(ParagraphStyle(
            name='TextoJustificado',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
    
    def _limpar_texto(self, texto: str) -> str:
        """Limpa e formata texto para o PDF"""
        if not texto:
            return "Texto não disponível"
        
        # Remover caracteres especiais problemáticos
        texto = re.sub(r'[^\w\s\-.,;:()!?áéíóúâêîôûàèìòùãõçÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]', '', texto)
        
        # Limitar tamanho
        if len(texto) > 1000:
            texto = texto[:1000] + "..."
        
        return texto.strip()
    
    def _gerar_capa(self) -> list:
        """Gera a capa do documento"""
        elementos = []
        
        # Título principal
        titulo = Paragraph("NORMAS TÉCNICAS ABNT", self.styles['TituloPrincipal'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.5*inch))
        
        # Subtítulo
        subtitulo = Paragraph("Normas Ambientais Brasileiras", self.styles['Subtitulo'])
        elementos.append(subtitulo)
        elementos.append(Spacer(1, 0.3*inch))
        
        # Descrição
        descricao = Paragraph(
            "Compilação de normas técnicas da Associação Brasileira de Normas Técnicas (ABNT) "
            "relacionadas ao meio ambiente, sustentabilidade e gestão ambiental.",
            self.styles['TextoJustificado']
        )
        elementos.append(descricao)
        elementos.append(Spacer(1, 0.5*inch))
        
        # Estatísticas
        total_normas = len(self.dados)
        
        # Contar por categoria
        categorias = {}
        anos = {}
        for norma in self.dados:
            cat = norma.get('categoria', 'Não especificada')
            categorias[cat] = categorias.get(cat, 0) + 1
            
            ano = norma.get('ano', 'N/A')
            if ano and ano != 'N/A':
                anos[ano] = anos.get(ano, 0) + 1
        
        # Tabela de estatísticas
        dados_tabela = [
            ['📊 ESTATÍSTICAS GERAIS', ''],
            ['Total de Normas', str(total_normas)],
            ['', ''],
            ['📋 POR CATEGORIA', ''],
        ]
        
        for categoria, count in sorted(categorias.items()):
            dados_tabela.append([categoria, str(count)])
        
        if anos:
            dados_tabela.append(['', ''])
            dados_tabela.append(['📅 POR ANO (Top 5)', ''])
            for ano, count in sorted(anos.items(), key=lambda x: x[1], reverse=True)[:5]:
                dados_tabela.append([ano, str(count)])
        
        tabela = Table(dados_tabela, colWidths=[3*inch, 1*inch])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('BACKGROUND', (0, 3), (-1, 3), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.5*inch))
        
        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        data_para = Paragraph(f"Documento gerado em: {data_geracao}", self.styles['Normal'])
        elementos.append(data_para)
        
        elementos.append(PageBreak())
        return elementos
    
    def _gerar_indice(self) -> list:
        """Gera índice das normas"""
        elementos = []
        
        titulo_indice = Paragraph("ÍNDICE DE NORMAS", self.styles['TituloSecao'])
        elementos.append(titulo_indice)
        elementos.append(Spacer(1, 0.2*inch))
        
        # Ordenar normas por código
        normas_ordenadas = sorted(self.dados, key=lambda x: x.get('codigo', ''))
        
        dados_indice = [['Código', 'Título', 'Ano']]
        
        for i, norma in enumerate(normas_ordenadas):
            codigo = norma.get('codigo', 'N/A')
            titulo = norma.get('titulo', 'Sem título')
            ano = norma.get('ano', 'N/A')
            
            # Truncar título se muito longo
            if len(titulo) > 60:
                titulo = titulo[:60] + "..."
            
            dados_indice.append([codigo, titulo, ano])
        
        tabela_indice = Table(dados_indice, colWidths=[2*inch, 3.5*inch, 0.8*inch])
        tabela_indice.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elementos.append(tabela_indice)
        elementos.append(PageBreak())
        
        return elementos
    
    def _gerar_normas(self) -> list:
        """Gera seção com todas as normas"""
        elementos = []
        
        titulo_normas = Paragraph("NORMAS TÉCNICAS ABNT", self.styles['TituloSecao'])
        elementos.append(titulo_normas)
        elementos.append(Spacer(1, 0.2*inch))
        
        # Ordenar normas por código
        normas_ordenadas = sorted(self.dados, key=lambda x: x.get('codigo', ''))
        
        for i, norma in enumerate(normas_ordenadas, 1):
            # Código da norma
            codigo = norma.get('codigo', 'N/A')
            codigo_para = Paragraph(f"{i}. {codigo}", self.styles['CodigoNorma'])
            elementos.append(codigo_para)
            
            # Título
            titulo = self._limpar_texto(norma.get('titulo', 'Sem título'))
            titulo_para = Paragraph(f"<b>Título:</b> {titulo}", self.styles['TextoJustificado'])
            elementos.append(titulo_para)
            
            # Metadados
            metadados = []
            
            status = norma.get('status', 'N/A')
            if status and status != 'N/A':
                metadados.append(f"<b>Status:</b> {status}")
            
            ano = norma.get('ano', 'N/A')
            if ano and ano != 'N/A':
                metadados.append(f"<b>Ano:</b> {ano}")
            
            categoria = norma.get('categoria', 'N/A')
            if categoria and categoria != 'N/A':
                metadados.append(f"<b>Categoria:</b> {categoria}")
            
            escopo = norma.get('escopo', 'N/A')
            if escopo and escopo != 'N/A':
                metadados.append(f"<b>Escopo:</b> {escopo}")
            
            comite = norma.get('comite', 'N/A')
            if comite and comite != 'N/A':
                metadados.append(f"<b>Comitê:</b> {comite}")
            
            preco = norma.get('preco', 'N/A')
            if preco and preco != 'N/A':
                metadados.append(f"<b>Preço:</b> {preco}")
            
            if metadados:
                metadados_texto = " | ".join(metadados)
                metadados_para = Paragraph(metadados_texto, self.styles['TextoJustificado'])
                elementos.append(metadados_para)
            
            # Resumo/Descrição
            resumo = norma.get('resumo', norma.get('text', ''))
            if resumo:
                resumo_limpo = self._limpar_texto(resumo)
                resumo_para = Paragraph(f"<b>Descrição:</b> {resumo_limpo}", self.styles['TextoJustificado'])
                elementos.append(resumo_para)
            
            # Data de coleta
            data_coleta = norma.get('collected_at', 'N/A')
            if data_coleta and data_coleta != 'N/A':
                try:
                    # Tentar formatar a data
                    if 'T' in data_coleta:
                        data_obj = datetime.fromisoformat(data_coleta.replace('Z', '+00:00'))
                        data_formatada = data_obj.strftime("%d/%m/%Y")
                        data_para = Paragraph(f"<b>Data de coleta:</b> {data_formatada}", self.styles['TextoJustificado'])
                        elementos.append(data_para)
                except:
                    pass
            
            elementos.append(Spacer(1, 0.2*inch))
            
            # Quebra de página a cada 3 normas para melhor legibilidade
            if i % 3 == 0 and i < len(normas_ordenadas):
                elementos.append(PageBreak())
        
        return elementos
    
    def gerar_pdf(self) -> str:
        """Gera o PDF consolidado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"ABNT_Normas_Ambientais_Consolidadas_{timestamp}.pdf"
        
        print(f"📄 Gerando PDF: {nome_arquivo}")
        
        # Criar documento
        pdf_doc = SimpleDocTemplate(
            nome_arquivo,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Construir conteúdo
        elementos = []
        
        print("📝 Gerando capa...")
        elementos.extend(self._gerar_capa())
        
        print("📋 Gerando índice...")
        elementos.extend(self._gerar_indice())
        
        print("📚 Gerando normas...")
        elementos.extend(self._gerar_normas())
        
        # Construir PDF
        print("🔨 Construindo PDF...")
        pdf_doc.build(elementos)
        
        # Verificar tamanho do arquivo
        arquivo_path = Path(nome_arquivo)
        if arquivo_path.exists():
            tamanho_mb = arquivo_path.stat().st_size / (1024 * 1024)
            print(f"✅ PDF gerado com sucesso!")
            print(f"📁 Arquivo: {nome_arquivo}")
            print(f"📊 Tamanho: {tamanho_mb:.2f} MB")
            print(f"📄 Total de normas: {len(self.dados)}")
            
            return nome_arquivo
        else:
            raise Exception("Arquivo PDF não foi criado")

def main():
    """Função principal"""
    
    # Procurar arquivo JSON mais recente da ABNT
    arquivos_json = list(Path('.').glob('abnt_normas_ambientais_*.json'))
    
    if not arquivos_json:
        print("❌ Nenhum arquivo JSON da ABNT encontrado!")
        print("💡 Execute primeiro o script 'extrair_dados_abnt.py'")
        return
    
    # Usar o arquivo mais recente
    arquivo_mais_recente = max(arquivos_json, key=lambda x: x.stat().st_mtime)
    
    print("🔧 GERADOR DE PDF - NORMAS ABNT")
    print("=" * 50)
    print(f"📂 Usando arquivo: {arquivo_mais_recente}")
    
    try:
        # Criar gerador e gerar PDF
        gerador = ABNTPDFGenerator(str(arquivo_mais_recente))
        
        if not gerador.dados:
            print("❌ Nenhum dado encontrado no arquivo JSON!")
            return
        
        nome_pdf = gerador.gerar_pdf()
        
        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📖 O PDF consolidado das normas ABNT está pronto!")
        print(f"📁 Localização: {nome_pdf}")
        
        # Estatísticas finais
        total_normas = len(gerador.dados)
        categorias = {}
        for norma in gerador.dados:
            cat = norma.get('categoria', 'Não especificada')
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Total de normas: {total_normas}")
        for categoria, count in sorted(categorias.items()):
            print(f"   • {categoria}: {count} normas")
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")

if __name__ == "__main__":
    main()