#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface web para o gerador de tabelas de leis ambientais
Usando Streamlit para uma interface mais amigável
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import json

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from ia_tabela_service import IATabela

# Configuração da página
st.set_page_config(
    page_title="IA Tabelas - Leis Ambientais",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado do tema
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def get_theme_css():
    """Retorna CSS baseado no tema atual"""
    if st.session_state.dark_mode:
        return """
        <style>
            /* Importar fontes modernas */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
            
            /* MODO ESCURO */
            .stApp {
                background-color: #0f172a !important;
                color: #e2e8f0;
            }
            
            /* Remover barra branca do topo */
            .css-18e3th9, .css-1d391kg, .css-k1vhr4, .css-1y4p8pa, 
            header[data-testid="stHeader"], .stHeader, [data-testid="stHeader"] {
                background-color: #0f172a !important;
            }
            
            /* Container principal */
            .css-k1vhr4, .css-18e3th9 {
                background-color: #0f172a !important;
            }
            
            /* Toolbar do Streamlit */
            .css-14xtw13, .css-1y4p8pa {
                background-color: #0f172a !important;
            }
            
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1200px;
                background-color: #0f172a;
            }
            
            /* Fonte global */
            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                color: #e2e8f0;
            }
            
            /* Header principal - Modo escuro */
            .main-header {
                background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
                padding: 2.5rem 2rem;
                border-radius: 20px;
                color: #f1f5f9;
                text-align: center;
                margin-bottom: 3rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .main-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.05) 50%, transparent 70%);
                animation: shimmer 3s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .main-header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                position: relative;
                z-index: 1;
                color: #f1f5f9;
            }
            
            .main-header h3 {
                font-size: 1.25rem;
                font-weight: 400;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                color: #cbd5e1;
            }
            
            /* Sidebar escura - Todos os seletores */
            .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-1y4p8pa, .css-1aumxhk, 
            section[data-testid="stSidebar"], .stSidebar, [data-testid="stSidebar"] {
                background-color: #1e293b !important;
                color: #e2e8f0 !important;
            }
            
            /* Texto da sidebar */
            .css-1d391kg *, .css-1lcbmhc *, .css-17eq0hr *, .css-1y4p8pa *, .css-1aumxhk *,
            section[data-testid="stSidebar"] *, .stSidebar *, [data-testid="stSidebar"] *,
            .css-1d391kg .stMarkdown, .css-1d391kg .stText, .css-1d391kg p, 
            .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, 
            .css-1d391kg h5, .css-1d391kg h6, .css-1d391kg span, .css-1d391kg div {
                color: #e2e8f0 !important;
            }
            
            /* Métricas na sidebar */
            .css-1d391kg .metric-container, .css-1d391kg [data-testid="metric-container"] {
                background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
                color: #e2e8f0 !important;
                border: 1px solid #64748b !important;
            }
            
            /* Botões na sidebar */
            .css-1d391kg .stButton > button {
                background: linear-gradient(135deg, #475569 0%, #334155 100%) !important;
                color: #f1f5f9 !important;
                border: 1px solid #64748b !important;
            }
            
            /* Cards e containers - Modo escuro */
            .success-box {
                background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
                border: 1px solid #059669;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
            
            .info-box {
                background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
                border: 1px solid #3b82f6;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
            
            /* Botões - Modo escuro */
            .stButton > button {
                background: linear-gradient(135deg, #475569 0%, #334155 100%);
                color: #f1f5f9;
                border: 1px solid #64748b;
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                font-weight: 500;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                background: linear-gradient(135deg, #64748b 0%, #475569 100%);
                border-color: #94a3b8;
            }
            
            /* Inputs - Modo escuro */
            .stTextArea > div > div > textarea {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 2px solid #475569;
                border-radius: 12px;
                transition: all 0.3s ease;
            }
            
            .stTextArea > div > div > textarea:focus {
                border-color: #64748b;
                box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.1);
            }
            
            .stSelectbox > div > div > select {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 2px solid #475569;
                border-radius: 12px;
            }
            
            /* Checkbox - Modo escuro */
            .stCheckbox > label {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: #e2e8f0;
                border: 2px solid #475569;
            }
            
            .stCheckbox > label:hover {
                border-color: #64748b;
                background: linear-gradient(135deg, #334155 0%, #475569 100%);
            }
            
            /* Métricas - Modo escuro */
            .metric-container {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border: 1px solid #475569;
                color: #e2e8f0;
            }
            
            /* DataFrames - Modo escuro */
            .stDataFrame {
                background-color: #1e293b;
                border: 1px solid #475569;
            }
            
            /* Texto geral */
            .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
                color: #e2e8f0;
            }
            
            /* Ícones */
            .icon, .icon-header, .icon-sidebar {
                color: #94a3b8;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Importar fontes modernas */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
            
            /* MODO CLARO */
            .stApp {
                background-color: #ffffff !important;
                color: #1f2937;
            }
            
            /* Remover barra branca do topo - Modo claro */
            .css-18e3th9, .css-1d391kg, .css-k1vhr4, .css-1y4p8pa, 
            header[data-testid="stHeader"], .stHeader, [data-testid="stHeader"] {
                background-color: #ffffff !important;
            }
            
            /* Container principal - Modo claro */
            .css-k1vhr4, .css-18e3th9 {
                background-color: #ffffff !important;
            }
            
            /* Toolbar do Streamlit - Modo claro */
            .css-14xtw13, .css-1y4p8pa {
                background-color: #ffffff !important;
            }
            
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }
            
            /* Fonte global */
            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            /* Header principal - Design moderno */
            .main-header {
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
                padding: 2.5rem 2rem;
                border-radius: 20px;
                color: white;
                text-align: center;
                margin-bottom: 3rem;
                box-shadow: 0 20px 40px rgba(59, 130, 246, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .main-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
                animation: shimmer 3s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .main-header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .main-header h3 {
                font-size: 1.25rem;
                font-weight: 400;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }
            
            /* Cards e containers */
            .success-box {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 1px solid #a7f3d0;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px rgba(16, 185, 129, 0.05);
            }
            
            .info-box {
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border: 1px solid #93c5fd;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.05);
            }
            
            /* Botões modernos */
            .stButton > button {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                font-weight: 500;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            }
            
            .stButton > button:active {
                transform: translateY(0);
            }
            
            /* Inputs modernos */
            .stTextArea > div > div > textarea {
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
                font-family: 'Inter', sans-serif;
            }
            
            .stTextArea > div > div > textarea:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .stSelectbox > div > div > select {
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
            }
            
            .stSelectbox > div > div > select:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            /* Checkbox moderno */
            .stCheckbox > label {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                padding: 1rem;
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .stCheckbox > label:hover {
                border-color: #3b82f6;
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            }
            
            /* Slider moderno */
            .stSlider > div > div > div > div {
                background: linear-gradient(90deg, #3b82f6, #06b6d4);
            }
            
            /* Métricas modernas */
            .metric-container {
                background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                padding: 1.5rem;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
                transition: all 0.3s ease;
            }
            
            .metric-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            }
            
            /* DataFrames modernos */
            .stDataFrame {
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
            }
    
    /* Headers de seção */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Spinner customizado */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Alertas modernos */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }
    
    /* Animações suaves */
    * {
        transition: all 0.3s ease;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header h3 {
            font-size: 1.1rem;
        }
        
        .main-header {
            padding: 2rem 1.5rem;
        }
    }
    
    /* Estilos para ícones profissionais */
    .icon {
        margin-right: 8px;
        color: #1f4e79;
        font-size: 1.1em;
    }
    
    .icon-header {
        margin-right: 12px;
        color: #ffffff;
        font-size: 1.3em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .icon-sidebar {
        margin-right: 8px;
        color: #2c5aa0;
        font-size: 1em;
    }
    
    .icon-button {
        margin-right: 6px;
        font-size: 0.9em;
    }
    
            .icon-metric {
                margin-right: 6px;
                color: #1f4e79;
                font-size: 1em;
            }
        </style>
        """

# Aplicar CSS baseado no tema
st.markdown(get_theme_css(), unsafe_allow_html=True)

def inicializar_ia():
    """Inicializa o serviço de IA com cache"""
    if 'ia_tabela' not in st.session_state:
        try:
            st.session_state.ia_tabela = IATabela()
            st.session_state.ia_inicializada = True
        except Exception as e:
            st.error(f"Erro ao inicializar IA: {e}")
            st.session_state.ia_inicializada = False
    
    return st.session_state.get('ia_inicializada', False)

def main():
    """Função principal da interface web"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-robot icon-header"></i>Plêiade Ambiental - Geradora de Tabelas</h1>
        <h3>Organizador Inteligente de Dados Ambientais</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar IA
    if not inicializar_ia():
        st.error("Não foi possível inicializar a IA. Verifique a configuração da API OpenAI.")
        return
    
    # Mostrar dados disponíveis (fora da sidebar para evitar erros)
    total_todas_fontes = len(st.session_state.ia_tabela.todas_fontes_data)
    total_leis = len(st.session_state.ia_tabela.leis_data)
    
    # Sidebar com informações
    with st.sidebar:
        # Toggle do modo escuro/claro
        st.markdown("### <i class='fas fa-palette icon-sidebar'></i>Tema", unsafe_allow_html=True)
        
        col_theme1, col_theme2 = st.columns(2)
        with col_theme1:
            if st.button("🌙 Escuro", use_container_width=True, key="dark_btn"):
                st.session_state.dark_mode = True
                st.rerun()
        
        with col_theme2:
            if st.button("☀️ Claro", use_container_width=True, key="light_btn"):
                st.session_state.dark_mode = False
                st.rerun()
        
        # Indicador do tema atual
        tema_atual = "🌙 Modo Escuro" if st.session_state.dark_mode else "☀️ Modo Claro"
        st.info(f"Tema atual: {tema_atual}")
        
        st.markdown("---")
        
        st.markdown("### <i class='fas fa-info-circle icon-sidebar'></i>Informações das Fontes", unsafe_allow_html=True)
        
        # Métricas das fontes
        st.metric("📊 Total Documentos", total_todas_fontes)
        
        st.markdown("### <i class='fas fa-database icon-sidebar'></i>Fontes Disponíveis:", unsafe_allow_html=True)
        fontes_info = {
            "Legislação Estadual TO": ("fas fa-landmark", "Leis ambientais do Tocantins"),
            "Power BI": ("fas fa-chart-line", "Dados de business intelligence"),
            "ABNT": ("fas fa-certificate", "Normas técnicas brasileiras"),
            "COEMA": ("fas fa-leaf", "Conselho Estadual do Meio Ambiente"),
            "CONAMA": ("fas fa-flag-usa", "Conselho Nacional do Meio Ambiente"),
            "IBAMA": ("fas fa-shield-alt", "Instituto Brasileiro do Meio Ambiente"),
            "ICMBio": ("fas fa-tree", "Instituto Chico Mendes")
        }
        
        for fonte, (icone, desc) in fontes_info.items():
            st.markdown(f"<i class='{icone} icon-sidebar'></i>**{fonte}**: {desc}", unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-lightbulb icon-sidebar'></i>Como usar:", unsafe_allow_html=True)
        st.markdown("""
        <i class='fas fa-edit icon-sidebar'></i>1. **Descreva** como quer organizar os dados<br>
        <i class='fas fa-check-square icon-sidebar'></i>2. **Escolha** fonte: só leis ou todas as fontes<br>
        <i class='fas fa-play icon-sidebar'></i>3. **Visualize** o resultado<br>
        <i class='fas fa-download icon-sidebar'></i>4. **Baixe** a tabela gerada
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-clipboard-list icon-sidebar'></i>Exemplos de descrições:", unsafe_allow_html=True)
        st.markdown("""
        <i class='fas fa-file-contract icon-sidebar'></i>"Organizar por fonte e jurisdição"<br>
        <i class='fas fa-certificate icon-sidebar'></i>"Tabela focada em normas técnicas"<br>
        <i class='fas fa-folder icon-sidebar'></i>"Agrupar por tipo de documento"<br>
        <i class='fas fa-file-alt icon-sidebar'></i>"Dados sobre licenciamento"<br>
        <i class='fas fa-balance-scale icon-sidebar'></i>"Comparar fontes federais e estaduais"
        """, unsafe_allow_html=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### <i class='fas fa-edit icon'></i>Descrição da Tabela", unsafe_allow_html=True)
        
        descricao = st.text_area(
            "Como você quer organizar os dados ambientais?",
            placeholder="Ex: Organizar por fonte, comparando dados federais e estaduais sobre licenciamento",
            height=100
        )
        
        # Opção para escolher fonte de dados
        incluir_todas_fontes = st.checkbox(
            "🌐 Incluir TODAS as fontes (Power BI, ABNT, COEMA, etc.)",
            value=True,
            help="Se marcado, inclui dados de todas as fontes. Se desmarcado, apenas leis estaduais do TO."
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            st.markdown("""
            <style>
            .stButton > button:first-child {
                background: linear-gradient(135deg, #2c5aa0 0%, #1f4e79 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .stButton > button:first-child:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(44, 90, 160, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            btn_vazia = st.button("📊 Gerar Tabela Vazia", use_container_width=True)
        
        with col_btn2:
            btn_dados = st.button("📋 Gerar com Dados", use_container_width=True)
    
    with col2:
        st.markdown("### <i class='fas fa-cog icon'></i>Configurações", unsafe_allow_html=True)
        
        if btn_dados:
            if incluir_todas_fontes:
                limite_documentos = st.slider("📊 Número de documentos", 5, 100, 20)
                st.info(f"📊 Incluindo dados de todas as fontes ({total_todas_fontes} disponíveis)")
            else:
                limite_documentos = st.slider("🏛️ Número de leis", 5, 50, 10)
                st.info(f"🏛️ Apenas leis estaduais do TO ({total_leis} disponíveis)")
        else:
            limite_documentos = 10
        
        formato_download = st.selectbox(
            "Formato para download",
            ["Excel", "CSV"],
            index=0
        )
    
    # Processamento
    if btn_vazia or btn_dados:
        if not descricao.strip():
            st.error("❌ Por favor, descreva como quer organizar a tabela!")
            return
        
        with st.spinner("🤖 Processando com IA direcionada..."):
            try:
                # Gerar estrutura
                estrutura = st.session_state.ia_tabela.gerar_estrutura_tabela(descricao)
                
                # Mostrar estrutura gerada
                st.success("✅ Estrutura da tabela gerada com sucesso!")
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.markdown(f"**<i class='fas fa-heading icon'></i>Título:** {estrutura['titulo_tabela']}", unsafe_allow_html=True)
                    st.markdown(f"**<i class='fas fa-align-left icon'></i>Descrição:** {estrutura['descricao']}", unsafe_allow_html=True)
                
                with col_info2:
                    st.markdown(f"**<i class='fas fa-filter icon'></i>Filtros:** {', '.join(estrutura.get('filtros_sugeridos', []))}", unsafe_allow_html=True)
                    st.markdown(f"**<i class='fas fa-sort icon'></i>Ordenação:** {estrutura.get('ordenacao_padrao', 'Não definida')}", unsafe_allow_html=True)
                
                # Mostrar colunas
                st.markdown("### <i class='fas fa-columns icon'></i>Estrutura das Colunas", unsafe_allow_html=True)
                
                colunas_df = pd.DataFrame(estrutura['colunas'])
                st.dataframe(colunas_df, use_container_width=True)
                
                # Gerar tabela
                if btn_vazia:
                    df_resultado = st.session_state.ia_tabela.gerar_tabela_vazia(estrutura)
                    st.markdown("### 📊 Tabela Vazia Gerada")
                else:
                    df_resultado = st.session_state.ia_tabela.popular_tabela(
                        estrutura, 
                        num_documentos=limite_documentos, 
                        incluir_todas_fontes=incluir_todas_fontes
                    )
                    
                    if incluir_todas_fontes:
                        st.markdown(f"### 📋 Tabela com {len(df_resultado)} Documentos de Todas as Fontes")
                    else:
                        st.markdown(f"### 📋 Tabela com {len(df_resultado)} Leis Estaduais")
                
                # Mostrar tabela
                st.dataframe(df_resultado, use_container_width=True)
                
                # Preparar dados para download
                from io import BytesIO
                excel_buffer = BytesIO()
                df_resultado.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                
                relatorio_md = st.session_state.ia_tabela.gerar_relatorio_tabela(estrutura, df_resultado)
                
                # Botões de download
                col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
                
                with col_dl1:
                    st.download_button(
                        "📊 Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"{estrutura['titulo_tabela']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col_dl2:
                    st.download_button(
                        "📄 CSV",
                        data=df_resultado.to_csv(index=False),
                        file_name=f"{estrutura['titulo_tabela']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col_dl3:
                    st.download_button(
                        "🔧 JSON (Estrutura)",
                        data=json.dumps(estrutura, indent=2, ensure_ascii=False),
                        file_name=f"{estrutura['titulo_tabela']}_estrutura.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col_dl4:
                    st.download_button(
                        "📋 Markdown (Relatório)",
                        data=relatorio_md,
                        file_name=f"{estrutura['titulo_tabela']}_relatorio.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                # Estatísticas da tabela
                st.markdown("### <i class='fas fa-chart-bar icon'></i>Estatísticas da Tabela", unsafe_allow_html=True)
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.metric("📊 Total de Linhas", len(df_resultado))
                
                with col_stat2:
                    st.metric("📋 Total de Colunas", len(df_resultado.columns))
                
                with col_stat3:
                    fontes_unicas = df_resultado['Fonte'].nunique() if 'Fonte' in df_resultado.columns else 0
                    st.metric("🌐 Fontes Diferentes", fontes_unicas)
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar tabela: {str(e)}")
                st.error("💡 Tente descrever de forma mais específica ou verifique se a API está configurada.")

# Rodapé
st.markdown("---")
st.markdown("**<i class='fas fa-robot icon'></i>IA Geradora de Tabelas** - Desenvolvido para análise de dados ambientais", unsafe_allow_html=True)
st.markdown("<i class='fas fa-lightbulb icon'></i>**Dica:** Seja específico na descrição para melhores resultados!", unsafe_allow_html=True)

if __name__ == "__main__":
    main()