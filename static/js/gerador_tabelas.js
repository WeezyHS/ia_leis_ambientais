// ===== GERADOR DE TABELAS - JAVASCRIPT =====
// Replicação das funcionalidades da interface Streamlit

class GeradorTabelas {
    constructor() {
        this.currentTheme = 'dark';
        this.currentMethod = 'detailed';
        this.isProcessing = false;
        this.lastResults = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDataSources();
        this.setupSliderSync();
        this.setupThemeToggle();
        this.setupMethodToggle();
        this.setupValidations();
    }
    
    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Botões principais
        document.getElementById('gerarEstrutura').addEventListener('click', () => {
            this.processRequest('estrutura');
        });
        
        document.getElementById('gerarQuadroResumo').addEventListener('click', () => {
            this.processRequest('quadro-resumo');
        });
        
        // Botões de download
        document.getElementById('downloadExcel').addEventListener('click', () => {
            this.downloadFile('excel');
        });
        
        document.getElementById('downloadCsv').addEventListener('click', () => {
            this.downloadFile('csv');
        });
        
        // Campo de descrição do projeto
        document.getElementById('projectDescription').addEventListener('input', 
            this.debounce(() => this.extractProjectInfo(), 1000)
        );
        
        // Validação em tempo real
        document.getElementById('projectDescription').addEventListener('blur', () => {
            this.validateProjectDescription();
        });
        
        document.getElementById('municipio').addEventListener('blur', () => {
            this.validateMunicipio();
        });
        
        document.getElementById('descricaoEmpreendimento').addEventListener('blur', () => {
            this.validateDescricaoEmpreendimento();
        });
    }
    
    // ===== TOGGLE DE TEMA =====
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const themeLabel = document.querySelector('.theme-label');
        const appContainer = document.querySelector('.app-container');
        
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                this.currentTheme = 'dark';
                appContainer.setAttribute('data-theme', 'dark');
                themeLabel.textContent = 'Modo Escuro';
            } else {
                this.currentTheme = 'light';
                appContainer.setAttribute('data-theme', 'light');
                themeLabel.textContent = 'Modo Claro';
            }
            
            // Salvar preferência
            localStorage.setItem('theme', this.currentTheme);
        });
        
        // Carregar tema salvo
        const savedTheme = localStorage.getItem('theme') || 'dark';
        if (savedTheme === 'light') {
            themeToggle.checked = false;
            themeToggle.dispatchEvent(new Event('change'));
        }
    }
    
    // ===== TOGGLE DE MÉTODO =====
    setupMethodToggle() {
        const toggleBtns = document.querySelectorAll('.toggle-btn');
        const detailedMethod = document.getElementById('detailedMethod');
        const manualMethod = document.getElementById('manualMethod');
        
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const method = btn.getAttribute('data-method');
                
                // Atualizar botões
                toggleBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Mostrar/ocultar métodos
                if (method === 'detailed') {
                    detailedMethod.style.display = 'block';
                    manualMethod.style.display = 'none';
                    this.currentMethod = 'detailed';
                } else {
                    detailedMethod.style.display = 'none';
                    manualMethod.style.display = 'block';
                    this.currentMethod = 'manual';
                }
            });
        });
    }
    
    // ===== SINCRONIZAÇÃO SLIDER/INPUT =====
    setupSliderSync() {
        const slider = document.getElementById('maxDocumentsSlider');
        const numberInput = document.getElementById('maxDocumentsNumber');
        
        slider.addEventListener('input', () => {
            numberInput.value = slider.value;
        });
        
        numberInput.addEventListener('input', () => {
            const value = Math.max(5, Math.min(50, parseInt(numberInput.value) || 5));
            numberInput.value = value;
            slider.value = value;
        });
    }
    
    // ===== VALIDAÇÕES =====
    setupValidations() {
        // Validação de relevância da descrição
        this.relevanciaKeywords = [
            'construção', 'instalação', 'operação', 'atividade', 'empreendimento',
            'projeto', 'obra', 'desenvolvimento', 'implantação', 'exploração',
            'produção', 'processamento', 'tratamento', 'disposição', 'armazenamento'
        ];
        
        // Validação anti-spam
        this.spamPatterns = [
            /(..)\1{4,}/g, // Caracteres repetidos
            /[^\w\s.,!?;:()\-]/g, // Caracteres especiais
            /(.)\1{10,}/g // Repetição excessiva
        ];
        
        // Mapeamento de atividades
        this.atividadeMapping = {
            'mineração': ['mineração', 'minério', 'extração', 'lavra', 'garimpo', 'carvão', 'ferro', 'ouro'],
            'energia': ['energia', 'elétrica', 'hidrelétrica', 'eólica', 'solar', 'termelétrica', 'usina', 'geração'],
            'industria': ['indústria', 'industrial', 'fábrica', 'manufatura', 'produção', 'processamento'],
            'agropecuaria': ['agropecuária', 'agricultura', 'pecuária', 'criação', 'cultivo', 'plantação', 'fazenda'],
            'infraestrutura': ['rodovia', 'estrada', 'ponte', 'túnel', 'ferrovia', 'porto', 'aeroporto', 'infraestrutura'],
            'turismo': ['turismo', 'hotel', 'pousada', 'resort', 'ecoturismo', 'turístico'],
            'residencial': ['residencial', 'habitação', 'condomínio', 'loteamento', 'casa', 'apartamento'],
            'comercial': ['comercial', 'shopping', 'loja', 'comércio', 'mercado', 'supermercado']
        };
    }
    
    // ===== EXTRAÇÃO DE INFORMAÇÕES DO PROJETO =====
    async extractProjectInfo() {
        const description = document.getElementById('projectDescription').value.trim();
        
        if (description.length < 20) {
            this.hideExtractedInfo();
            return;
        }
        
        try {
            // Extrair município
            const municipio = this.extractMunicipio(description);
            
            // Extrair atividade
            const atividade = this.extractAtividade(description);
            
            if (municipio || atividade) {
                this.showExtractedInfo(municipio, atividade);
            } else {
                this.hideExtractedInfo();
            }
            
        } catch (error) {
            console.error('Erro ao extrair informações:', error);
        }
    }
    
    extractMunicipio(text) {
        // Padrões para identificar municípios
        const patterns = [
            /(?:município|cidade|localizada?|situado?)\s+(?:de|em|no|na)?\s+([A-ZÁÊÇÕ][a-záêçõ\s]+)/gi,
            /(?:em|no|na)\s+([A-ZÁÊÇÕ][a-záêçõ\s]+),?\s*(?:estado|[A-Z]{2})/gi,
            /([A-ZÁÊÇÕ][a-záêçõ\s]+),?\s*(?:estado|[A-Z]{2})/gi
        ];
        
        for (const pattern of patterns) {
            const matches = text.match(pattern);
            if (matches) {
                const municipio = matches[0].replace(/^(?:município|cidade|localizada?|situado?|em|no|na)\s+(?:de|em|no|na)?\s*/gi, '')
                                           .replace(/,?\s*(?:estado|[A-Z]{2}).*$/gi, '')
                                           .trim();
                if (municipio.length > 2) {
                    return this.capitalizeWords(municipio);
                }
            }
        }
        
        return null;
    }
    
    extractAtividade(text) {
        const textLower = text.toLowerCase();
        
        for (const [categoria, keywords] of Object.entries(this.atividadeMapping)) {
            for (const keyword of keywords) {
                if (textLower.includes(keyword)) {
                    return categoria;
                }
            }
        }
        
        return null;
    }
    
    showExtractedInfo(municipio, atividade) {
        const extractedInfo = document.getElementById('extractedInfo');
        const municipioSpan = document.getElementById('extractedMunicipio');
        const atividadeSpan = document.getElementById('extractedAtividade');
        
        municipioSpan.textContent = municipio || 'Não identificado';
        atividadeSpan.textContent = this.getAtividadeLabel(atividade) || 'Não identificada';
        
        extractedInfo.style.display = 'block';
        extractedInfo.classList.add('fade-in');
        
        // Auto-preencher campos manuais se estiverem vazios
        if (municipio && !document.getElementById('municipio').value) {
            document.getElementById('municipio').value = municipio;
        }
        
        if (atividade && !document.getElementById('atividade').value) {
            document.getElementById('atividade').value = atividade;
        }
    }
    
    hideExtractedInfo() {
        const extractedInfo = document.getElementById('extractedInfo');
        extractedInfo.style.display = 'none';
    }
    
    getAtividadeLabel(atividade) {
        const labels = {
            'mineracao': 'Mineração',
            'energia': 'Energia',
            'industria': 'Indústria',
            'agropecuaria': 'Agropecuária',
            'infraestrutura': 'Infraestrutura',
            'turismo': 'Turismo',
            'residencial': 'Residencial',
            'comercial': 'Comercial',
            'outros': 'Outros'
        };
        
        return labels[atividade] || atividade;
    }
    
    // ===== VALIDAÇÕES DE ENTRADA =====
    validateProjectDescription() {
        const description = document.getElementById('projectDescription').value.trim();
        
        if (!this.validarRelevanciaDescricao(description)) {
            this.showError('A descrição deve conter informações relevantes sobre o projeto (localização, atividade, características).');
            return false;
        }
        
        if (!this.validarAntiSpam(description)) {
            this.showError('A descrição contém caracteres ou padrões inválidos.');
            return false;
        }
        
        return true;
    }
    
    validateMunicipio() {
        const municipio = document.getElementById('municipio').value.trim();
        
        if (this.currentMethod === 'manual' && municipio.length < 2) {
            this.showError('Por favor, informe um município válido.');
            return false;
        }
        
        return true;
    }
    
    validateDescricaoEmpreendimento() {
        const descricao = document.getElementById('descricaoEmpreendimento').value.trim();
        
        if (descricao && !this.validarAntiSpam(descricao)) {
            this.showError('A descrição do empreendimento contém caracteres inválidos.');
            return false;
        }
        
        return true;
    }
    
    validarRelevanciaDescricao(texto) {
        if (texto.length < 20) return false;
        
        const textoLower = texto.toLowerCase();
        const hasRelevantKeyword = this.relevanciaKeywords.some(keyword => 
            textoLower.includes(keyword)
        );
        
        const hasLocation = /(?:município|cidade|estado|localizada?|situado?)/.test(textoLower);
        
        return hasRelevantKeyword || hasLocation;
    }
    
    validarAntiSpam(texto) {
        for (const pattern of this.spamPatterns) {
            if (pattern.test(texto)) {
                return false;
            }
        }
        
        return true;
    }
    
    // ===== PROCESSAMENTO DE REQUISIÇÕES =====
    async processRequest(type) {
        if (this.isProcessing) return;
        
        // Validar entrada
        if (!this.validateInput()) {
            return;
        }
        
        this.isProcessing = true;
        this.showLoading();
        this.hideMessages();
        
        try {
            const requestData = this.buildRequestData(type);
            
            const endpoint = type === 'estrutura' ? '/api/gerar-estrutura' : '/api/gerar-quadro-resumo';
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.lastResults = result.data;
                this.showResults(result.data, type);
                this.showSuccess(`${type === 'estrutura' ? 'Estrutura' : 'Quadro-resumo'} gerado com sucesso!`);
            } else {
                throw new Error(result.message || 'Erro desconhecido');
            }
            
        } catch (error) {
            console.error('Erro ao processar requisição:', error);
            this.showError(`Erro ao gerar ${type}: ${error.message}`);
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    validateInput() {
        if (this.currentMethod === 'detailed') {
            const description = document.getElementById('projectDescription').value.trim();
            if (!description) {
                this.showError('Por favor, descreva seu projeto.');
                return false;
            }
            
            if (!this.validateProjectDescription()) {
                return false;
            }
        } else {
            const municipio = document.getElementById('municipio').value.trim();
            const atividade = document.getElementById('atividade').value;
            
            if (!municipio) {
                this.showError('Por favor, informe o município.');
                return false;
            }
            
            if (!atividade) {
                this.showError('Por favor, selecione o tipo de atividade.');
                return false;
            }
            
            if (!this.validateMunicipio()) {
                return false;
            }
        }
        
        // Validar esferas selecionadas
        const federal = document.getElementById('federal').checked;
        const estadual = document.getElementById('estadual').checked;
        const municipal = document.getElementById('municipal').checked;
        
        if (!federal && !estadual && !municipal) {
            this.showError('Por favor, selecione pelo menos uma esfera legal.');
            return false;
        }
        
        return true;
    }
    
    buildRequestData(type) {
        const data = {
            tipo: type,
            metodo: this.currentMethod
        };
        
        if (this.currentMethod === 'detailed') {
            data.descricao_projeto = document.getElementById('projectDescription').value.trim();
        } else {
            data.municipio = document.getElementById('municipio').value.trim();
            data.atividade = document.getElementById('atividade').value;
        }
        
        data.descricao_empreendimento = document.getElementById('descricaoEmpreendimento').value.trim();
        
        data.esferas = {
            federal: document.getElementById('federal').checked,
            estadual: document.getElementById('estadual').checked,
            municipal: document.getElementById('municipal').checked
        };
        
        data.max_documentos = parseInt(document.getElementById('maxDocumentsNumber').value);
        data.formato_download = document.getElementById('downloadFormat').value;
        
        return data;
    }
    
    // ===== EXIBIÇÃO DE RESULTADOS =====
    showResults(data, type) {
        const resultsSection = document.getElementById('resultsSection');
        const tableContent = document.getElementById('tableContent');
        const statsSection = document.getElementById('statsSection');
        
        // Criar tabela
        const table = this.createTable(data.tabela);
        tableContent.innerHTML = '';
        tableContent.appendChild(table);
        
        // Mostrar estatísticas se for quadro-resumo
        if (type === 'quadro-resumo' && data.estatisticas) {
            this.showStats(data.estatisticas);
            statsSection.style.display = 'block';
        } else {
            statsSection.style.display = 'none';
        }
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    createTable(data) {
        const table = document.createElement('table');
        
        // Cabeçalho
        if (data.length > 0) {
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            Object.keys(data[0]).forEach(key => {
                const th = document.createElement('th');
                th.textContent = this.formatColumnName(key);
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // Corpo
        const tbody = document.createElement('tbody');
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value || '-';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        
        return table;
    }
    
    formatColumnName(name) {
        const columnNames = {
            'lei': 'Lei',
            'artigo': 'Artigo',
            'descricao': 'Descrição',
            'esfera': 'Esfera',
            'tipo': 'Tipo',
            'relevancia': 'Relevância',
            'aplicabilidade': 'Aplicabilidade',
            'observacoes': 'Observações'
        };
        
        return columnNames[name] || name.charAt(0).toUpperCase() + name.slice(1);
    }
    
    showStats(stats) {
        document.getElementById('totalLegislacoes').textContent = stats.total || 0;
        document.getElementById('totalFederais').textContent = stats.federais || 0;
        document.getElementById('totalEstaduais').textContent = stats.estaduais || 0;
        document.getElementById('totalMunicipais').textContent = stats.municipais || 0;
    }
    
    // ===== DOWNLOAD DE ARQUIVOS =====
    async downloadFile(format) {
        if (!this.lastResults) {
            this.showError('Nenhum resultado disponível para download.');
            return;
        }
        
        try {
            const response = await fetch('/api/download-tabela', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dados: this.lastResults,
                    formato: format,
                    nome_arquivo: `tabela_legislacao_${new Date().toISOString().slice(0, 10)}`
                })
            });
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            a.href = url;
            a.download = `tabela_legislacao_${new Date().toISOString().slice(0, 10)}.${format === 'excel' ? 'xlsx' : 'csv'}`;
            
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            window.URL.revokeObjectURL(url);
            
            this.showSuccess(`Arquivo ${format.toUpperCase()} baixado com sucesso!`);
            
        } catch (error) {
            console.error('Erro ao baixar arquivo:', error);
            this.showError(`Erro ao baixar arquivo: ${error.message}`);
        }
    }
    
    // ===== CARREGAMENTO DE DADOS =====
    async loadDataSources() {
        try {
            const response = await fetch('/api/fontes-dados');
            
            if (response.ok) {
                const data = await response.json();
                this.updateDataSources(data);
            }
        } catch (error) {
            console.error('Erro ao carregar fontes de dados:', error);
        }
    }
    
    updateDataSources(data) {
        document.getElementById('federalCount').textContent = data.federal || 0;
        document.getElementById('estadualCount').textContent = data.estadual || 0;
        document.getElementById('municipalCount').textContent = data.municipal || 0;
        document.getElementById('totalCount').textContent = data.total || 0;
    }
    
    // ===== MENSAGENS E LOADING =====
    showLoading() {
        document.getElementById('loading').style.display = 'block';
        this.setButtonsDisabled(true);
    }
    
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        this.setButtonsDisabled(false);
    }
    
    showSuccess(message) {
        const successMessage = document.getElementById('successMessage');
        const successText = document.getElementById('successText');
        
        successText.textContent = message;
        successMessage.style.display = 'flex';
        successMessage.classList.add('fade-in');
        
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000);
    }
    
    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
        errorMessage.classList.add('fade-in');
        
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 8000);
    }
    
    hideMessages() {
        document.getElementById('successMessage').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';
    }
    
    setButtonsDisabled(disabled) {
        document.getElementById('gerarEstrutura').disabled = disabled;
        document.getElementById('gerarQuadroResumo').disabled = disabled;
    }
    
    // ===== UTILITÁRIOS =====
    capitalizeWords(str) {
        return str.replace(/\w\S*/g, (txt) => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
    new GeradorTabelas();
});

// ===== RESPONSIVIDADE MOBILE =====
function setupMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (window.innerWidth <= 768) {
        // Adicionar botão de menu mobile se necessário
        if (!document.querySelector('.mobile-menu-btn')) {
            const menuBtn = document.createElement('button');
            menuBtn.className = 'mobile-menu-btn';
            menuBtn.innerHTML = '☰';
            menuBtn.style.cssText = `
                position: fixed;
                top: 1rem;
                left: 1rem;
                z-index: 1000;
                background: var(--accent-color);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0.5rem;
                font-size: 1.25rem;
                cursor: pointer;
            `;
            
            menuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
            
            document.body.appendChild(menuBtn);
        }
    }
}

window.addEventListener('resize', setupMobileMenu);
setupMobileMenu();