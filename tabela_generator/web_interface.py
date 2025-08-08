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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
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
                color: #e2e8f0 !important;
            }
            
            /* Ocultar menu de configurações do Streamlit */
            button[title="View fullscreen"], 
            button[aria-label="View fullscreen"],
            [data-testid="stToolbar"],
            .css-14xtw13.e8zbici0,
            .css-vk3wp9,
            .css-1kyxreq > .css-fblp2m,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7 > .css-1wivap2,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7 > .css-1wivap2 > .css-1lcbmhc {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Sidebar - Modo escuro */
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div,
            [data-testid="stSidebar"] > div, [data-testid="stSidebar"] > div > div,
            .css-1544g2n, .css-1d391kg > div, .css-1d391kg > div > div {
                background-color: #0f172a !important;
                color: #e2e8f0 !important;
            }
            
            /* Corrigir bordas e separadores pretos */
            .css-1kyxreq::before, .css-12oz5g7::before, .css-1v0mbdj::before,
            .css-16huue1::before, .css-1inwz65::before, .css-1cpxqw2::before,
            .css-1vencpc::before, .css-1y4p8pa::before, .css-1lcbmhc::before,
            .css-17eq0hr::before, .css-1aumxhk::before, .css-1d391kg::before {
                background-color: #1e293b !important;
                border-color: #334155 !important;
            }
            
            /* Corrigir elementos de interface pretos */
            .css-1kyxreq *, .css-12oz5g7 *, .css-1v0mbdj *, .css-16huue1 *,
            .css-1inwz65 *, .css-1cpxqw2 *, .css-1vencpc *, .css-1y4p8pa *,
            .css-1lcbmhc *, .css-17eq0hr *, .css-1aumxhk *, .css-1d391kg *,
            [data-testid="stSidebar"] *, [data-testid="stSidebar"] > div *,
            .css-1544g2n *, .css-1d391kg > div *, .css-1d391kg > div > div * {
                color: #e2e8f0 !important;
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
            
            /* Inputs - Modo escuro - Correção ULTRA específica */
            /* TextArea - Todos os seletores possíveis */
            .stTextArea textarea,
            .stTextArea > div > div > textarea,
            textarea[data-testid="stTextArea"],
            [data-testid="stTextArea"] textarea,
            [data-testid="stTextArea"] > div > div > textarea,
            div[data-testid="stTextArea"] textarea,
            div[data-testid="stTextArea"] > div > div > textarea,
            .css-1cpxqw2 textarea,
            .css-1d391kg textarea,
            .css-16huue1 textarea,
            .css-1v0mbdj textarea,
            .css-12oz5g7 textarea,
            .css-1kyxreq textarea {
                background-color: #1e293b !important;
                background: #1e293b !important;
                color: #e2e8f0 !important;
                border: 2px solid #475569 !important;
                border-radius: 12px !important;
                transition: all 0.3s ease !important;
                font-size: 14px !important;
                line-height: 1.5 !important;
                padding: 12px !important;
                font-family: 'Inter', sans-serif !important;
                -webkit-text-fill-color: #e2e8f0 !important;
                opacity: 1 !important;
            }
            
            /* Focus states */
            .stTextArea textarea:focus,
            .stTextArea > div > div > textarea:focus,
            textarea[data-testid="stTextArea"]:focus,
            [data-testid="stTextArea"] textarea:focus,
            [data-testid="stTextArea"] > div > div > textarea:focus,
            div[data-testid="stTextArea"] textarea:focus,
            div[data-testid="stTextArea"] > div > div > textarea:focus,
            .css-1cpxqw2 textarea:focus,
            .css-1d391kg textarea:focus,
            .css-16huue1 textarea:focus,
            .css-1v0mbdj textarea:focus,
            .css-12oz5g7 textarea:focus,
            .css-1kyxreq textarea:focus {
                border-color: #64748b !important;
                box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.1) !important;
                background-color: #1e293b !important;
                background: #1e293b !important;
                color: #e2e8f0 !important;
                -webkit-text-fill-color: #e2e8f0 !important;
                outline: none !important;
            }
            
            /* Placeholder text */
            .stTextArea textarea::placeholder,
            textarea[data-testid="stTextArea"]::placeholder {
                color: #94a3b8 !important;
                opacity: 0.7 !important;
            }
            
            /* Containers das caixas de texto - Modo escuro */
            .stTextArea,
            .stTextArea > div,
            .stTextArea > div > div,
            [data-testid="stTextArea"],
            [data-testid="stTextArea"] > div,
            [data-testid="stTextArea"] > div > div,
            div[data-testid="stTextArea"],
            div[data-testid="stTextArea"] > div,
            div[data-testid="stTextArea"] > div > div {
                background-color: transparent !important;
                background: transparent !important;
            }
            
            .stSelectbox > div > div > select,
            .stSelectbox select,
            select[data-testid="stSelectbox"],
            [data-testid="stSelectbox"] > div > div > select,
            [data-testid="stSelectbox"] select {
                background-color: #1e293b !important;
                color: #e2e8f0 !important;
                border: 2px solid #475569 !important;
                border-radius: 12px !important;
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
            
            /* Corrigir fundo interno da checkbox no modo escuro */
            body.dark-mode div[data-testid="stCheckbox"] input[type="checkbox"] {
                accent-color: #0ea5e9 !important; /* azul claro */
                background-color: #1e293b !important;
                border: 2px solid #475569 !important;
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
                color: #1f2937 !important;
            }
            
            /* Ocultar menu de configurações do Streamlit */
            button[title="View fullscreen"], 
            button[aria-label="View fullscreen"],
            [data-testid="stToolbar"],
            .css-14xtw13.e8zbici0,
            .css-vk3wp9,
            .css-1kyxreq > .css-fblp2m,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7 > .css-1wivap2,
            .css-1kyxreq > .css-fblp2m > .css-1wivap2 > .css-1lcbmhc > .css-1outpf7 > .css-1wivap2 > .css-1lcbmhc {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Sidebar - Modo claro */
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div,
            [data-testid="stSidebar"] > div, [data-testid="stSidebar"] > div > div,
            .css-1544g2n, .css-1d391kg > div, .css-1d391kg > div > div {
                background-color: #ffffff !important;
                color: #1f2937 !important;
            }
            
            /* Corrigir bordas e separadores pretos - Modo claro */
            .css-1kyxreq::before, .css-12oz5g7::before, .css-1v0mbdj::before,
            .css-16huue1::before, .css-1inwz65::before, .css-1cpxqw2::before,
            .css-1vencpc::before, .css-1y4p8pa::before, .css-1lcbmhc::before,
            .css-17eq0hr::before, .css-1aumxhk::before, .css-1d391kg::before {
                background-color: #f1f5f9 !important;
                border-color: #e2e8f0 !important;
            }
            
            /* Corrigir elementos de interface pretos - Modo claro */
            .css-1kyxreq *, .css-12oz5g7 *, .css-1v0mbdj *, .css-16huue1 *,
            .css-1inwz65 *, .css-1cpxqw2 *, .css-1vencpc *, .css-1y4p8pa *,
            .css-1lcbmhc *, .css-17eq0hr *, .css-1aumxhk *, .css-1d391kg *,
            [data-testid="stSidebar"] *, [data-testid="stSidebar"] > div *,
            .css-1544g2n *, .css-1d391kg > div *, .css-1d391kg > div > div * {
                color: #1f2937 !important;
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
            
            /* Inputs modernos - Correção ULTRA específica */
            /* TextArea - Todos os seletores possíveis - Modo claro */
            .stTextArea textarea,
            .stTextArea > div > div > textarea,
            textarea[data-testid="stTextArea"],
            [data-testid="stTextArea"] textarea,
            [data-testid="stTextArea"] > div > div > textarea,
            div[data-testid="stTextArea"] textarea,
            div[data-testid="stTextArea"] > div > div > textarea,
            .css-1cpxqw2 textarea,
            .css-1d391kg textarea,
            .css-16huue1 textarea,
            .css-1v0mbdj textarea,
            .css-12oz5g7 textarea,
            .css-1kyxreq textarea {
                background-color: #ffffff !important;
                background: #ffffff !important;
                color: #1f2937 !important;
                border: 2px solid #e2e8f0 !important;
                border-radius: 12px !important;
                transition: all 0.3s ease !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                line-height: 1.5 !important;
                padding: 12px !important;
                -webkit-text-fill-color: #1f2937 !important;
                opacity: 1 !important;
            }
            
            /* Focus states - Modo claro */
            .stTextArea textarea:focus,
            .stTextArea > div > div > textarea:focus,
            textarea[data-testid="stTextArea"]:focus,
            [data-testid="stTextArea"] textarea:focus,
            [data-testid="stTextArea"] > div > div > textarea:focus,
            div[data-testid="stTextArea"] textarea:focus,
            div[data-testid="stTextArea"] > div > div > textarea:focus,
            .css-1cpxqw2 textarea:focus,
            .css-1d391kg textarea:focus,
            .css-16huue1 textarea:focus,
            .css-1v0mbdj textarea:focus,
            .css-12oz5g7 textarea:focus,
            .css-1kyxreq textarea:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
                background-color: #ffffff !important;
                background: #ffffff !important;
                color: #1f2937 !important;
                -webkit-text-fill-color: #1f2937 !important;
                outline: none !important;
            }
            
            /* Placeholder text - Modo claro */
            .stTextArea textarea::placeholder,
            textarea[data-testid="stTextArea"]::placeholder {
                color: #6b7280 !important;
                opacity: 0.7 !important;
            }
            
            /* Containers das caixas de texto - Modo claro */
            .stTextArea,
            .stTextArea > div,
            .stTextArea > div > div,
            [data-testid="stTextArea"],
            [data-testid="stTextArea"] > div,
            [data-testid="stTextArea"] > div > div,
            div[data-testid="stTextArea"],
            div[data-testid="stTextArea"] > div,
            div[data-testid="stTextArea"] > div > div {
                background-color: transparent !important;
                background: transparent !important;
            }
            
            /* ===== CORREÇÕES ESPECÍFICAS PARA MODO CLARO ===== */
            
            /* 1. Corrigir cor dos labels e textos gerais */
            .stRadio label, .stRadio span, label, span, .css-1cpxqw2 label, .css-1cpxqw2 span {
                color: #1f2937 !important;
            }
            
            /* 2. Correção para selectbox com classes padrão do Streamlit */
            .css-1cpxqw2 select,
            .css-16huue1 select,
            .css-1v0mbdj select,
            .css-12oz5g7 select {
                background-color: #ffffff !important;
                color: #1f2937 !important;
                border: 2px solid #e2e8f0 !important;
                border-radius: 12px !important;
            }
            
            /* 3. Garantir que toda tipografia no modo claro seja visível */
            html, body, [class*="css"], label, span, div, p, h1, h2, h3, h4, h5, h6 {
                color: #1f2937 !important;
            }
            
            /* 4. FORÇA MÁXIMA - Checkboxes BRANCAS no modo claro */
            html body .stApp .stCheckbox > label, 
            html body .stApp .stCheckbox > label > div, 
            html body .stApp .stCheckbox > label > div > div,
            html body .stApp .stCheckbox > label span, 
            html body .stApp .stCheckbox label, 
            html body .stApp .stCheckbox span,
            html body .stApp [data-testid="stCheckbox"] label, 
            html body .stApp [data-testid="stCheckbox"] span,
            html body .stApp [data-testid="stCheckbox"] > label, 
            html body .stApp [data-testid="stCheckbox"] > label > div,
            html body .stApp div[data-testid="stCheckbox"] > label,
            html body .stApp div[data-testid="stCheckbox"] > label > div {
                color: #1f2937 !important;
                background-color: #ffffff !important;
                background: #ffffff !important;
                background-image: none !important;
                border: 2px solid #e2e8f0 !important;
            }
            
            /* Corrigir fundo interno da checkbox no modo claro */
            div[data-testid="stCheckbox"] input[type="checkbox"] {
                accent-color: #3b82f6 !important; /* cor azul padrão, pode mudar */
                background-color: #ffffff !important;
                border: 2px solid #e2e8f0 !important;
            }
            
            /* 5. FORÇA TOTAL - Sobrescrever QUALQUER gradiente escuro */
             html body .stApp .stCheckbox > label[style*="background"],
             html body .stApp .stCheckbox > label[style*="linear-gradient"] {
                 background: #ffffff !important;
                 background-color: #ffffff !important;
                 background-image: none !important;
             }
            
            /* Selectbox - Modo claro */
            .stSelectbox > div > div > select,
            .stSelectbox select,
            select[data-testid="stSelectbox"],
            [data-testid="stSelectbox"] > div > div > select,
            [data-testid="stSelectbox"] select {
                background-color: #ffffff !important;
                color: #1f2937 !important;
                border: 2px solid #e2e8f0 !important;
                border-radius: 12px !important;
                transition: all 0.3s ease !important;
            }
            
            .stSelectbox > div > div > select:focus,
            .stSelectbox select:focus,
            select[data-testid="stSelectbox"]:focus,
            [data-testid="stSelectbox"] > div > div > select:focus,
            [data-testid="stSelectbox"] select:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
                background-color: #ffffff !important;
                color: #1f2937 !important;
            }
            

            
            /* Checkbox moderno - Modo claro */
            .stCheckbox > label {
                background: #ffffff !important;
                color: #1f2937 !important;
                padding: 1rem !important;
                border-radius: 12px !important;
                border: 2px solid #e2e8f0 !important;
                transition: all 0.3s ease !important;
                cursor: pointer !important;
            }
            
            .stCheckbox > label:hover {
                border-color: #3b82f6 !important;
                background: #f8fafc !important;
                color: #1f2937 !important;
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
    
    # ⚠️ Destaque das premissas obrigatórias
    st.info("⚠️ **PREMISSAS OBRIGATÓRIAS**: Este sistema lista APENAS legislações vigentes com títulos oficiais completos. Legislações revogadas ou substituídas são automaticamente omitidas.")
    
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
        <i class='fas fa-map-marker-alt icon-sidebar'></i>1. **Selecione** o município do empreendimento<br>
        <i class='fas fa-industry icon-sidebar'></i>2. **Escolha** o grupo de atividade<br>
        <i class='fas fa-cog icon-sidebar'></i>3. **Configure** as esferas legais desejadas<br>
        <i class='fas fa-play icon-sidebar'></i>4. **Gere** a estrutura e depois o quadro-resumo<br>
        <i class='fas fa-download icon-sidebar'></i>5. **Baixe** o resultado nos formatos disponíveis
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-exclamation-triangle icon-sidebar'></i>Premissas obrigatórias:", unsafe_allow_html=True)
        st.markdown("""
        <i class='fas fa-check-circle icon-sidebar'></i>**APENAS legislações VIGENTES** são listadas<br>
        <i class='fas fa-file-alt icon-sidebar'></i>**Títulos oficiais** completos e status de vigência<br>
        <i class='fas fa-ban icon-sidebar'></i>**Legislações revogadas/substituídas** são omitidas<br>
        <i class='fas fa-balance-scale icon-sidebar'></i>Organizado por **esfera legal** (Federal, Estadual, Municipal)
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-target icon-sidebar'></i>Objetivo:", unsafe_allow_html=True)
        st.markdown("""
        **Quadro-resumo de legislações ambientais** aplicáveis a empreendimentos no Tocantins, 
        organizadas por esfera legal e específicas para o município e atividade selecionados.
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-clipboard-list icon-sidebar'></i>Características do quadro:", unsafe_allow_html=True)
        st.markdown("""
        <i class='fas fa-leaf icon-sidebar'></i>Específico para **legislações ambientais**<br>
        <i class='fas fa-map icon-sidebar'></i>Focado no **estado do Tocantins**<br>
        <i class='fas fa-bullseye icon-sidebar'></i>Adaptado para **município e atividade** selecionados<br>
        <i class='fas fa-clock icon-sidebar'></i>Dados atualizados e **status de vigência** verificado
        """, unsafe_allow_html=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### <i class='fas fa-map-marker-alt icon'></i>Localização e Atividade", unsafe_allow_html=True)
        
        col_input1, col_input2 = st.columns(2)
        
        # Lista de municípios do Tocantins
        municipios_tocantins = [
            "Palmas", "Araguaína", "Gurupi", "Porto Nacional", "Paraíso do Tocantins",
            "Colinas do Tocantins", "Guaraí", "Tocantinópolis", "Formoso do Araguaia",
            "Dianópolis", "Miracema do Tocantins", "Taguatinga", "Augustinópolis",
            "Pedro Afonso", "Xambioá", "Alvorada", "Arraias", "Araguatins",
            "Cristalândia", "Nova Olinda", "Ananás", "Outro município"
        ]
        
        # Opção de modo de entrada
        modo_entrada = st.radio(
            "🎯 Modo de Entrada:",
            options=["Comando Detalhado", "Seleção Manual"],
            help="Escolha como deseja fornecer as informações do empreendimento"
        )
        
        if modo_entrada == "Comando Detalhado":
            st.markdown("### 📝 Descreva seu Projeto")
            st.success("🎯 **Modo Inteligente Ativado:** Descreva seu projeto em linguagem natural e a IA extrairá automaticamente todas as informações necessárias!")
            
            # Exemplo expandido
            with st.expander("📋 Ver Exemplo de Comando", expanded=False):
                st.markdown("""
                **Exemplo de comando completo:**
                
                *"Estou fazendo um estudo ambiental para regularizar a atividade de agricultura do município de Ananás no Tocantins, elabore um quadro com a legislação ambiental federal, estadual e municipal relacionada ao tipo de empreendimento no contexto de um licenciamento ambiental"*
                
                **A IA identificará automaticamente:**
                - 📍 **Município:** Ananás
                - 🏭 **Atividade:** Agricultura  
                - ⚖️ **Esferas:** Federal, Estadual, Municipal
                - 📋 **Contexto:** Licenciamento ambiental
                """)
            
            # Campo para comando em linguagem natural
            comando_usuario = st.text_area(
                "💬 Descreva seu projeto em linguagem natural:",
                placeholder='Exemplo: "Estou fazendo um estudo ambiental para regularizar a atividade de agricultura do município de Ananás no Tocantins, elabore um quadro com a legislação ambiental federal, estadual e municipal relacionada ao tipo de empreendimento no contexto de um licenciamento ambiental"',
                height=150,
                help="Descreva seu projeto, município, atividade e contexto em linguagem natural. Seja específico sobre o tipo de empreendimento e o contexto (licenciamento, regularização, etc.)"
            )
            
            # Extrair informações automaticamente se o comando foi fornecido
            municipio_extraido = ""
            atividade_extraida = ""
            
            if comando_usuario:
                # Extrair município
                for mun in municipios_tocantins:
                    if mun.lower() in comando_usuario.lower():
                        municipio_extraido = mun
                        break
                
                # Extrair atividade
                atividades_map = {
                    "agricultura": "Agricultura", "agrícola": "Agricultura", "agropecuária": "Agricultura",
                    "pecuária": "Pecuária", "gado": "Pecuária", "bovino": "Pecuária", "suíno": "Pecuária",
                    "indústria": "Indústria", "industrial": "Indústria", "fábrica": "Indústria",
                    "mineração": "Mineração", "minério": "Mineração", "extração": "Mineração",
                    "saneamento": "Saneamento", "água": "Saneamento", "esgoto": "Saneamento",
                    "energia": "Energia", "elétrica": "Energia", "solar": "Energia", "eólica": "Energia"
                }
                
                for palavra, atividade in atividades_map.items():
                    if palavra in comando_usuario.lower():
                        atividade_extraida = atividade
                        break
            
            # Mostrar informações extraídas
            if comando_usuario:
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.info(f"🏙️ **Município identificado:** {municipio_extraido or 'Não identificado'}")
                with col_info2:
                    st.info(f"🏭 **Atividade identificada:** {atividade_extraida or 'Não identificada'}")
            
            # Usar valores extraídos ou permitir correção manual
            with col_input1:
                municipio = st.selectbox(
                    "🏛️ Confirme o Município:",
                    municipios_tocantins,
                    index=municipios_tocantins.index(municipio_extraido) if municipio_extraido in municipios_tocantins else 0,
                    help="Confirme ou corrija o município identificado"
                )
            
            with col_input2:
                atividades = [
                    "Agricultura", "Pecuária", "Indústria", "Mineração", 
                    "Saneamento", "Lazer e Turismo", "Energia", "Transporte",
                    "Construção Civil", "Serviços", "Comércio", "Outros"
                ]
                grupo_atividade = st.selectbox(
                    "🏭 Confirme a Atividade:",
                    atividades,
                    index=atividades.index(atividade_extraida) if atividade_extraida in atividades else 0,
                    help="Confirme ou corrija a atividade identificada"
                )
            
            # Usar o comando como descrição adicional
            descricao = comando_usuario
            
        else:
            # Modo de seleção manual (interface original)
            with col_input1:
                municipio = st.selectbox(
                    "🏛️ Município do Tocantins",
                    municipios_tocantins,
                    index=0,
                    help="Selecione o município onde será desenvolvido o empreendimento"
                )
            
            with col_input2:
                grupo_atividade = st.selectbox(
                    "🏭 Grupo de Atividade",
                    [
                        "Agricultura", "Pecuária", "Indústria", "Mineração", 
                        "Saneamento", "Lazer e Turismo", "Energia", "Transporte",
                        "Construção Civil", "Serviços", "Comércio", "Outros"
                    ],
                    index=0,
                    help="Selecione o tipo de atividade do empreendimento"
                )
            
            st.markdown("### <i class='fas fa-edit icon'></i>Descrição Adicional (Opcional)", unsafe_allow_html=True)
            
            descricao = st.text_area(
                "Informações específicas sobre o empreendimento (opcional)",
                placeholder="Ex: Frigorífico de grande porte, Usina hidrelétrica, Loteamento residencial...",
                height=80,
                help="Informações adicionais que podem ajudar na seleção de legislações mais específicas"
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
            btn_estrutura = st.button("📋 Gerar Estrutura", use_container_width=True)
        
        with col_btn2:
            btn_quadro = st.button("⚖️ Gerar Quadro-Resumo", use_container_width=True)
    
    with col2:
        st.markdown("### <i class='fas fa-cog icon'></i>Configurações", unsafe_allow_html=True)
        
        incluir_esferas = st.multiselect(
            "⚖️ Esferas Legais",
            ["Federal", "Estadual", "Municipal"],
            default=["Federal", "Estadual", "Municipal"]
        )
        
        limite_documentos = st.slider("📊 Máximo de legislações por esfera", 5, 20, 10)
        st.info(f"🏛️ Base: {total_leis} leis estaduais do TO disponíveis")
        
        formato_download = st.selectbox(
            "Formato para download",
            ["Excel", "CSV"],
            index=0
        )
    
    # Processamento
    if btn_estrutura or btn_quadro:
        # Validação básica
        if not municipio or not grupo_atividade:
            st.error("❌ Por favor, selecione o município e grupo de atividade!")
            return
        
        if btn_estrutura:
            with st.spinner("🔄 Gerando estrutura do quadro-resumo..."):
                try:
                    estrutura = st.session_state.ia_tabela.gerar_quadro_resumo_legislacoes(
                        municipio=municipio,
                        grupo_atividade=grupo_atividade,
                        descricao_adicional=descricao,
                        esferas_legais=incluir_esferas,
                        comando_natural=(modo_entrada == "Comando Detalhado")
                    )
                    
                    if estrutura:
                        st.session_state.estrutura_atual = estrutura
                        st.success("✅ Estrutura do quadro-resumo gerada com sucesso!")
                        
                        # Exibir estrutura
                        st.subheader("📋 Estrutura do Quadro-Resumo")
                        st.json(estrutura)
                    else:
                        st.error("❌ Erro ao gerar estrutura do quadro-resumo")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao gerar estrutura: {str(e)}")
        
        elif btn_quadro:
            with st.spinner("🔄 Gerando quadro-resumo completo..."):
                try:
                    # Se não há estrutura, gerar automaticamente
                    if 'estrutura_atual' not in st.session_state:
                        st.info("🔄 Gerando estrutura automaticamente...")
                        estrutura = st.session_state.ia_tabela.gerar_quadro_resumo_legislacoes(
                            municipio=municipio,
                            grupo_atividade=grupo_atividade,
                            descricao_adicional=descricao,
                            esferas=incluir_esferas,
                            comando_natural=(modo_entrada == "Comando Detalhado")
                        )
                        st.session_state.estrutura_atual = estrutura
                    
                    # Gerar o quadro-resumo populado
                    df_resultado = st.session_state.ia_tabela.popular_quadro_resumo(
                        estrutura=st.session_state.estrutura_atual,
                        municipio=municipio,
                        grupo_atividade=grupo_atividade,
                        esferas=incluir_esferas,
                        limite_por_esfera=limite_documentos
                    )
                    
                    if df_resultado is not None and not df_resultado.empty:
                        st.session_state.df_resultado = df_resultado
                        st.success("✅ Quadro-resumo gerado com sucesso!")
                        
                        # Exibir título da tabela
                        st.subheader(f"📊 Quadro-Resumo de Legislações Ambientais - {municipio}")
                        st.caption(f"**Atividade:** {grupo_atividade} | **Esferas:** {', '.join(incluir_esferas)} | **Total:** {len(df_resultado)} legislações")
                        
                        # Exibir tabela
                        st.dataframe(
                            df_resultado,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "esfera": st.column_config.TextColumn("🏛️ Esfera", width="small"),
                                "titulo_legislacao": st.column_config.TextColumn("📜 Título da Legislação", width="large"),
                                "vigencia": st.column_config.TextColumn("⚖️ Vigência", width="small"),
                                "descricao_resumida": st.column_config.TextColumn("📝 Descrição Resumida", width="large"),
                                "aplicabilidade": st.column_config.TextColumn("🎯 Aplicabilidade", width="large")
                            }
                        )
                    else:
                        st.error("❌ Erro ao gerar quadro-resumo com dados")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao gerar quadro-resumo: {str(e)}")
        
        # Mostrar downloads se houver resultado
        if 'df_resultado' in st.session_state and not st.session_state.df_resultado.empty:
            df_resultado = st.session_state.df_resultado
                
            # Preparar dados para download
            from io import BytesIO
            excel_buffer = BytesIO()
            df_resultado.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            
            # Botões de download
            st.markdown("### <i class='fas fa-download icon'></i>Downloads", unsafe_allow_html=True)
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                st.download_button(
                    "📊 Baixar Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"quadro_resumo_{municipio}_{grupo_atividade}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col_dl2:
                st.download_button(
                    "📄 Baixar CSV",
                    data=df_resultado.to_csv(index=False),
                    file_name=f"quadro_resumo_{municipio}_{grupo_atividade}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Estatísticas da tabela
            st.markdown("### <i class='fas fa-chart-bar icon'></i>Estatísticas do Quadro-Resumo", unsafe_allow_html=True)
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("📊 Total de Legislações", len(df_resultado))
            
            with col_stat2:
                esferas_unicas = df_resultado['esfera'].nunique() if 'esfera' in df_resultado.columns else 0
                st.metric("🏛️ Esferas Representadas", esferas_unicas)
            
            with col_stat3:
                st.metric("📋 Total de Colunas", len(df_resultado.columns))

# Rodapé
st.markdown("---")
st.markdown("**<i class='fas fa-robot icon'></i>IA Geradora de Tabelas** - Desenvolvido para análise de dados ambientais", unsafe_allow_html=True)
st.markdown("<i class='fas fa-lightbulb icon'></i>**Dica:** Seja específico na descrição para melhores resultados!", unsafe_allow_html=True)

if __name__ == "__main__":
    main()