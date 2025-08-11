#!/usr/bin/env python3
"""
Interface Web com Integração LexML
=================================

Versão atualizada da interface web que utiliza dados oficiais
da API do LexML em vez de dados pré-definidos.

PRINCIPAIS MUDANÇAS:
- Usa IATabela_ComLexML em vez de IATabela
- Mostra fonte dos dados (LexML vs Pré-definidos)
- Indicadores de status da API
- Opções de atualização de cache
- Logs em tempo real

Autor: Sistema IA Leis Ambientais
Data: 2025
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime
import time

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'services'))

# Configuração da página
st.set_page_config(
    page_title="IA Leis Ambientais - Com LexML",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #228B22);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .lei-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    
    .fonte-oficial {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .fonte-fallback {
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def carregar_servico_lexml():
    """Carrega o serviço LexML"""
    try:
        from ia_tabela_service_lexml import ia_tabela_lexml
        return ia_tabela_lexml, True
    except ImportError as e:
        st.error(f"❌ Erro ao carregar serviço LexML: {e}")
        return None, False

def mostrar_header():
    """Mostra o cabeçalho da aplicação"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🌿 IA Leis Ambientais - Versão LexML</h1>
        <p>Sistema de Consulta de Legislação Ambiental com Dados Oficiais</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_status_sistema(servico):
    """Mostra o status do sistema e da integração LexML"""
    
    st.sidebar.markdown("## 📊 Status do Sistema")
    
    if servico:
        info_sistema = servico.get_info_sistema()
        
        # Status LexML
        if info_sistema.get('lexml_disponivel', False):
            st.sidebar.markdown("""
            <div class="status-card">
                <strong>🌐 LexML API</strong><br>
                ✅ Conectado e Funcionando
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""
            <div class="warning-card">
                <strong>🌐 LexML API</strong><br>
                ⚠️ Indisponível - Usando Fallback
            </div>
            """, unsafe_allow_html=True)
        
        # Estatísticas
        st.sidebar.markdown("### 📈 Estatísticas")
        st.sidebar.write(f"📚 Leis Estaduais: {info_sistema.get('leis_estaduais_carregadas', 0)}")
        st.sidebar.write(f"💾 Cache Federal: {info_sistema.get('cache_federal_size', 0)} leis")
        
        # Cache LexML
        if 'cache_lexml_stats' in info_sistema:
            stats_cache = info_sistema['cache_lexml_stats']
            st.sidebar.write(f"🗄️ Arquivos Cache: {stats_cache.get('total_arquivos', 0)}")
            st.sidebar.write(f"💽 Tamanho Cache: {stats_cache.get('tamanho_mb', 0)} MB")
        
        # Botão de atualização
        if st.sidebar.button("🔄 Atualizar Cache Federal"):
            with st.spinner("Atualizando cache..."):
                servico.atualizar_cache_federal()
            st.sidebar.success("✅ Cache atualizado!")
            st.experimental_rerun()
    
    else:
        st.sidebar.markdown("""
        <div class="error-card">
            <strong>❌ Sistema</strong><br>
            Erro ao carregar serviços
        </div>
        """, unsafe_allow_html=True)

def mostrar_formulario():
    """Mostra o formulário de entrada"""
    
    st.markdown("## 📋 Gerar Tabela de Legislação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        municipio = st.selectbox(
            "🏙️ Município",
            ["Palmas", "Araguaína", "Gurupi", "Porto Nacional", "Paraíso do Tocantins", 
             "Colinas do Tocantins", "Guaraí", "Tocantinópolis", "Formoso do Araguaia"],
            index=0
        )
        
        grupo_atividade = st.selectbox(
            "🏭 Grupo de Atividade",
            ["Agricultura", "Pecuária", "Indústria", "Mineração", "Saneamento", "Energia"],
            index=0
        )
    
    with col2:
        incluir_federais = st.checkbox("🇧🇷 Incluir Legislações Federais", value=True)
        incluir_estaduais = st.checkbox("🏛️ Incluir Legislações Estaduais", value=True)
        incluir_municipais = st.checkbox("🏢 Incluir Legislações Municipais", value=False)
        
        limite_por_esfera = st.slider("📊 Limite por Esfera", min_value=1, max_value=20, value=10)
    
    return {
        'municipio': municipio,
        'grupo_atividade': grupo_atividade,
        'incluir_federais': incluir_federais,
        'incluir_estaduais': incluir_estaduais,
        'incluir_municipais': incluir_municipais,
        'limite_por_esfera': limite_por_esfera
    }

def mostrar_legislacao(legislacao, index):
    """Mostra uma legislação individual"""
    
    # Determinar classe CSS baseada na fonte
    fonte_dados = legislacao.get('fonte_dados', '')
    if 'LexML' in fonte_dados:
        fonte_class = "fonte-oficial"
        fonte_icon = "🌐"
    else:
        fonte_class = "fonte-fallback"
        fonte_icon = "📝"
    
    st.markdown(f"""
    <div class="lei-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #007bff;">
                {index}. {legislacao['titulo_legislacao']}
            </h4>
            <span class="{fonte_class}">
                {fonte_icon} {fonte_dados}
            </span>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <strong>📝 Descrição Resumida:</strong><br>
            {legislacao['descricao_resumida']}
        </div>
        
        <div style="margin-bottom: 1rem;">
            <strong>⚖️ Aplicabilidade:</strong><br>
            {legislacao['aplicabilidade']}
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span><strong>🏛️ Esfera:</strong> {legislacao['esfera']}</span>
            <span><strong>✅ Vigência:</strong> {legislacao['vigencia']}</span>
        </div>
        
        {f'<div style="margin-top: 0.5rem;"><strong>🔗 URL Oficial:</strong> <a href="{legislacao["url_oficial"]}" target="_blank">{legislacao["url_oficial"]}</a></div>' if legislacao.get('url_oficial') else ''}
    </div>
    """, unsafe_allow_html=True)

def mostrar_resultados(tabela):
    """Mostra os resultados da consulta"""
    
    st.markdown("## 📊 Resultados da Consulta")
    
    # Informações gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total de Legislações", tabela['total_legislacoes'])
    
    with col2:
        fonte_federal = tabela.get('fonte_dados_federais', 'N/A')
        cor_fonte = "🌐" if "LexML" in fonte_federal else "📝"
        st.metric("🇧🇷 Fonte Federal", f"{cor_fonte} {fonte_federal}")
    
    with col3:
        st.metric("📅 Data Geração", tabela['data_geracao'])
    
    with col4:
        municipio = tabela['municipio']
        atividade = tabela['grupo_atividade']
        st.metric("🎯 Consulta", f"{municipio} - {atividade}")
    
    # Estatísticas detalhadas
    if 'estatisticas' in tabela:
        st.markdown("### 📈 Estatísticas Detalhadas")
        
        stats = tabela['estatisticas']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Por Esfera:**")
            for esfera, count in stats.get('por_esfera', {}).items():
                st.write(f"• {esfera}: {count} legislações")
        
        with col2:
            st.markdown("**🔍 Por Fonte de Dados:**")
            for fonte, count in stats.get('por_fonte_dados', {}).items():
                icon = "🌐" if "LexML" in fonte else "📝"
                st.write(f"• {icon} {fonte}: {count}")
    
    # Separar por esfera
    legislacoes = tabela['legislacoes']
    
    federais = [leg for leg in legislacoes if leg['esfera'] == 'Federal']
    estaduais = [leg for leg in legislacoes if leg['esfera'] == 'Estadual']
    municipais = [leg for leg in legislacoes if leg['esfera'] == 'Municipal']
    
    # Mostrar legislações federais
    if federais:
        st.markdown("### 🇧🇷 Legislações Federais")
        for i, leg in enumerate(federais, 1):
            mostrar_legislacao(leg, i)
    
    # Mostrar legislações estaduais
    if estaduais:
        st.markdown("### 🏛️ Legislações Estaduais")
        for i, leg in enumerate(estaduais, 1):
            mostrar_legislacao(leg, i)
    
    # Mostrar legislações municipais
    if municipais:
        st.markdown("### 🏢 Legislações Municipais")
        for i, leg in enumerate(municipais, 1):
            mostrar_legislacao(leg, i)

def mostrar_comparacao_fontes(servico, parametros):
    """Mostra comparação entre dados LexML e pré-definidos"""
    
    if st.button("🔍 Comparar com Dados Pré-definidos"):
        with st.spinner("Comparando fontes de dados..."):
            
            # Gerar com LexML
            tabela_lexml = servico.gerar_tabela_legislacao(**parametros)
            
            # Tentar gerar com dados originais
            try:
                sys.path.append('.')
                from ia_tabela_service import IATabela
                
                ia_original = IATabela()
                tabela_original = ia_original.gerar_tabela_legislacao(**parametros)
                
                st.markdown("### 🔄 Comparação de Fontes")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📝 Dados Pré-definidos")
                    federais_orig = [leg for leg in tabela_original['legislacoes'] if leg['esfera'] == 'Federal']
                    
                    for i, leg in enumerate(federais_orig[:3], 1):
                        st.markdown(f"""
                        **{i}. {leg['titulo_legislacao'][:50]}...**
                        
                        📝 {leg['descricao_resumida'][:100]}...
                        """)
                
                with col2:
                    st.markdown("#### 🌐 Dados LexML")
                    federais_lexml = [leg for leg in tabela_lexml['legislacoes'] if leg['esfera'] == 'Federal']
                    
                    for i, leg in enumerate(federais_lexml[:3], 1):
                        fonte_icon = "🌐" if "LexML" in leg.get('fonte_dados', '') else "📝"
                        st.markdown(f"""
                        **{i}. {leg['titulo_legislacao'][:50]}...**
                        
                        {fonte_icon} {leg['descricao_resumida'][:100]}...
                        """)
                
            except Exception as e:
                st.warning(f"⚠️ Não foi possível comparar: {e}")

def exportar_resultados(tabela):
    """Permite exportar os resultados"""
    
    st.markdown("### 📤 Exportar Resultados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Exportar JSON"):
            json_data = json.dumps(tabela, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"legislacao_{tabela['municipio']}_{tabela['grupo_atividade']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Exportar CSV"):
            import pandas as pd
            
            df = pd.DataFrame(tabela['legislacoes'])
            csv_data = df.to_csv(index=False, encoding='utf-8')
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"legislacao_{tabela['municipio']}_{tabela['grupo_atividade']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Copiar Resumo"):
            resumo = f"""
LEGISLAÇÃO AMBIENTAL - {tabela['municipio']} - {tabela['grupo_atividade']}
Data: {tabela['data_geracao']}
Total: {tabela['total_legislacoes']} legislações
Fonte Federal: {tabela.get('fonte_dados_federais', 'N/A')}

LEGISLAÇÕES:
"""
            for i, leg in enumerate(tabela['legislacoes'], 1):
                resumo += f"{i}. {leg['titulo_legislacao']}\n"
                resumo += f"   {leg['descricao_resumida'][:100]}...\n\n"
            
            st.text_area("📋 Resumo para Copiar", resumo, height=200)

def main():
    """Função principal da aplicação"""
    
    # Mostrar header
    mostrar_header()
    
    # Carregar serviço
    servico, sucesso = carregar_servico_lexml()
    
    if not sucesso:
        st.error("❌ Não foi possível carregar o serviço LexML. Verifique a instalação.")
        return
    
    # Mostrar status na sidebar
    mostrar_status_sistema(servico)
    
    # Formulário principal
    parametros = mostrar_formulario()
    
    # Botão de geração
    if st.button("🚀 Gerar Tabela de Legislação", type="primary"):
        
        with st.spinner("🔍 Consultando legislação ambiental..."):
            
            # Mostrar progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Buscando leis federais na API LexML...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("📚 Carregando leis estaduais...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("🏢 Processando leis municipais...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            # Gerar tabela
            try:
                tabela = servico.gerar_tabela_legislacao(**parametros)
                
                status_text.text("✅ Tabela gerada com sucesso!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Limpar indicadores de progresso
                progress_bar.empty()
                status_text.empty()
                
                # Mostrar resultados
                mostrar_resultados(tabela)
                
                # Opções adicionais
                st.markdown("---")
                
                # Comparação com dados originais
                mostrar_comparacao_fontes(servico, parametros)
                
                # Exportar resultados
                exportar_resultados(tabela)
                
                # Salvar na sessão para reutilização
                st.session_state['ultima_tabela'] = tabela
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Erro ao gerar tabela: {e}")
                
                # Mostrar detalhes do erro em modo debug
                if st.checkbox("🐛 Mostrar detalhes do erro"):
                    import traceback
                    st.code(traceback.format_exc())
    
    # Mostrar informações sobre a versão
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sobre esta Versão")
    st.sidebar.markdown("""
    **🌟 Novidades:**
    - ✅ Dados oficiais da API LexML
    - ✅ Cache para performance
    - ✅ Fallback automático
    - ✅ Logs detalhados
    - ✅ Comparação de fontes
    
    **📊 Versão:** IATabela_ComLexML v1.0
    """)

if __name__ == "__main__":
    main()