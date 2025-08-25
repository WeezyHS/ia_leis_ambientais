// /TESTE_chat_o3_e_o3-mini_Rogerio/js/chat_o3.js
// Versão adaptada para testar modelo o3
document.addEventListener('DOMContentLoaded', () => {
    const messageForm   = document.getElementById('message-form');
    const messageInput  = document.getElementById('message-input');
    const messagesArea  = document.getElementById('chat-messages');
    const newChatBtn    = document.querySelector('.new-chat-btn');
    const chatList      = document.getElementById('chat-list');
  
    // Memória em runtime (some ao recarregar a página).
    const conversations = new Map(); // key: conversation_id (ou temp id), value: { id, title, messages: [{role,content}] }
    let currentConversationKey = null; // pode ser um temp id até o backend devolver o UUID
  
    // Utils
    const uid = () => 'temp_' + Math.random().toString(36).slice(2, 10);
  
    const clearMessagesUI = () => {
      messagesArea.innerHTML = '';
    };
  
    const renderMessages = (history) => {
      clearMessagesUI();
      history.forEach(m => addMessageToUI(m.role, m.content));
      messagesArea.scrollTop = messagesArea.scrollHeight;
    };
  
    const addMessageToUI = (role, content) => {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${role}`;
  
      const avatar = document.createElement('div');
      avatar.className = 'avatar';
      avatar.textContent = role === 'user' ? '👤' : '🧠'; // Emoji diferente para o3
  
      const textDiv = document.createElement('div');
      textDiv.className = 'text';
      textDiv.textContent = content;
  
      messageDiv.appendChild(avatar);
      messageDiv.appendChild(textDiv);
      messagesArea.appendChild(messageDiv);
    };
  
    const setActiveListItem = (li) => {
      [...chatList.querySelectorAll('li')].forEach(el => el.classList.remove('active'));
      if (li) li.classList.add('active');
    };
  
    const createListItem = (title, key, backendId = null) => {
      const li = document.createElement('li');
      const titleSpan = document.createElement('span');
      titleSpan.textContent = title || 'Novo chat';
      titleSpan.className = 'chat-title';

      const editIcon = document.createElement('span');
      editIcon.innerHTML = '✏️';
      editIcon.className = 'edit-chat-icon';
      editIcon.title = 'Editar nome';

      const deleteIcon = document.createElement('span');
      deleteIcon.className = 'delete-chat-icon';
      deleteIcon.innerHTML = '🗑️';
      deleteIcon.title = 'Excluir chat';

      const a = document.createElement('a');
      a.href = '#';
      a.appendChild(titleSpan);
      
      const actionsContainer = document.createElement('div');
      actionsContainer.className = 'chat-actions-container';
      actionsContainer.appendChild(editIcon);
      actionsContainer.appendChild(deleteIcon);
      
      a.appendChild(actionsContainer);

      li.appendChild(a);
      li.dataset.key = key;
      if (backendId) li.dataset.id = backendId;

      a.addEventListener('click', (e) => {
        e.preventDefault();
        currentConversationKey = key;
        const conv = conversations.get(key);
        if (conv) {
          renderMessages(conv.messages);
          setActiveListItem(li);
        }
      });

      chatList.prepend(li);
      setActiveListItem(li);
      return li;
    };
  
    const updateListItemTitle = (key, title) => {
      const li = chatList.querySelector(`li[data-key="${CSS.escape(key)}"]`);
      if (li) {
        li.querySelector('.chat-title').textContent = title;
      }
      const conv = conversations.get(key);
      if (conv) conv.title = title;
    };
  
    const attachBackendIdToItem = (key, backendId) => {
      const li = chatList.querySelector(`li[data-key="${CSS.escape(key)}"]`);
      if (li) {
        li.dataset.id = backendId;
      }
      const conv = conversations.get(key);
      if (conv) conv.id = backendId;
    };
  
    // Fluxo de "Novo Chat"
    const startNewChat = () => {
      const tempKey = uid();
  
      conversations.set(tempKey, {
        id: null,
        title: 'Novo chat o3',
        messages: [{ role: 'assistant', content: '🧠 Olá! Sou o modelo o3 da OpenAI. Como posso ajudar você hoje?' }]
      });
  
      createListItem('Novo chat o3', tempKey, null);
  
      currentConversationKey = tempKey;
      renderMessages(conversations.get(tempKey).messages);
    };
  
    newChatBtn.addEventListener('click', startNewChat);
  
    // Envio de mensagem
    const handleSendMessage = async (event) => {
      event.preventDefault();
      const userMessage = messageInput.value.trim();
      if (!userMessage) return;
  
      if (!currentConversationKey) {
        startNewChat();
      }
  
      const conv = conversations.get(currentConversationKey);
      conv.messages.push({ role: 'user', content: userMessage });
      addMessageToUI('user', userMessage);
      messageInput.value = '';
  
      if (conv.title === 'Novo chat o3') {
        const short = userMessage.length > 28 ? userMessage.slice(0, 28) + '…' : userMessage;
        updateListItemTitle(currentConversationKey, short || 'Novo chat o3');
      }
  
      try {
        const body = {
          history: conv.messages,
          conversation_id: conv.id ?? null
        };
  
        const response = await fetch('/ask-ia-o3', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
  
        if (!response.ok) throw new Error('A resposta do servidor não foi OK');
  
        const data = await response.json();
        const aiResponse = data.response;
  
        if (data.conversation_id && !conv.id) {
          conv.id = data.conversation_id;
          attachBackendIdToItem(currentConversationKey, data.conversation_id);
        }
  
        conv.messages.push({ role: 'assistant', content: aiResponse });
        addMessageToUI('assistant', aiResponse);
  
      } catch (error) {
        console.error('Erro ao comunicar com a IA o3:', error);
        conv.messages.push({ role: 'assistant', content: 'Desculpe, ocorreu um erro ao tentar conectar-me ao modelo o3.' });
        addMessageToUI('assistant', 'Desculpe, ocorreu um erro ao tentar conectar-me ao modelo o3.');
      }
    };
  
    messageForm.addEventListener('submit', handleSendMessage);

    messageInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage(event);
      }
    });

    // Funcionalidade do botão Documentos
    const documentosButton = document.getElementById('documentos-button');
    if (documentosButton) {
      documentosButton.addEventListener('click', () => {
        showDocumentUploadModal();
      });
    }

    // Função para mostrar modal de upload de documentos
    const showDocumentUploadModal = () => {
      // Cria o modal dinamicamente
      const modal = document.createElement('div');
      modal.className = 'document-upload-modal';
      modal.innerHTML = `
        <div class="modal-content">
          <div class="modal-header">
            <h3>Upload de Documento</h3>
            <span class="close-modal">&times;</span>
          </div>
          <div class="modal-body">
            <div class="upload-area" id="upload-area">
              <div class="upload-icon">📄</div>
              <p>Arraste um arquivo PDF aqui ou clique para selecionar</p>
              <input type="file" id="file-input" accept=".pdf" style="display: none;">
              <button type="button" id="select-file-btn" class="select-file-btn">Selecionar Arquivo</button>
            </div>
            <div class="upload-progress" id="upload-progress" style="display: none;">
              <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
              </div>
              <p id="progress-text">Processando documento...</p>
            </div>
            <div class="upload-result" id="upload-result" style="display: none;"></div>
          </div>
        </div>
      `;

      document.body.appendChild(modal);

      // Event listeners do modal
      const closeModal = modal.querySelector('.close-modal');
      const fileInput = modal.querySelector('#file-input');
      const selectFileBtn = modal.querySelector('#select-file-btn');
      const uploadArea = modal.querySelector('#upload-area');
      const progressDiv = modal.querySelector('#upload-progress');
      const resultDiv = modal.querySelector('#upload-result');

      // Fechar modal
      closeModal.addEventListener('click', () => {
        document.body.removeChild(modal);
      });

      // Fechar modal clicando fora
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          document.body.removeChild(modal);
        }
      });

      // Botão selecionar arquivo
      selectFileBtn.addEventListener('click', () => {
        fileInput.click();
      });

      // Área de drag and drop
      uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
      });

      uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
      });

      uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
          handleFileUpload(files[0]);
        }
      });

      // Input de arquivo
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
          handleFileUpload(e.target.files[0]);
        }
      });

      // Função para processar upload
      const handleFileUpload = async (file) => {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
          alert('Por favor, selecione apenas arquivos PDF.');
          return;
        }

        // Mostra progresso
        uploadArea.style.display = 'none';
        progressDiv.style.display = 'block';

        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await fetch('/documents/upload', {
            method: 'POST',
            body: formData
          });

          const result = await response.json();

          if (response.ok && result.success) {
            // Sucesso
            progressDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
              <div class="upload-success">
                <div class="success-icon">✅</div>
                <h4>Documento processado com sucesso!</h4>
                <p><strong>Arquivo:</strong> ${result.filename}</p>
                <p><strong>Tamanho:</strong> ${formatFileSize(result.size)}</p>
                <p><strong>Texto extraído:</strong> ${result.text_length} caracteres</p>
                <p><strong>Chunks gerados:</strong> ${result.num_chunks}</p>
                <div class="preview">
                  <h5>Prévia do conteúdo:</h5>
                  <p class="preview-text">${result.preview}</p>
                </div>
                <div class="document-ready">
                  <p><strong>✨ Documento disponível para chat!</strong></p>
                  <p>Agora você pode fazer perguntas sobre este documento diretamente no chat.</p>
                  <button type="button" class="close-modal-btn" onclick="closeDocumentModal()">Fechar e Continuar</button>
                </div>
              </div>
            `;
          } else {
            // Erro
            progressDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
              <div class="upload-error">
                <div class="error-icon">❌</div>
                <h4>Erro ao processar documento</h4>
                <p>${result.detail || 'Erro desconhecido'}</p>
                <button type="button" class="retry-btn" onclick="location.reload()">Tentar Novamente</button>
              </div>
            `;
          }
        } catch (error) {
          console.error('Erro no upload:', error);
          progressDiv.style.display = 'none';
          resultDiv.style.display = 'block';
          resultDiv.innerHTML = `
            <div class="upload-error">
              <div class="error-icon">❌</div>
              <h4>Erro de conexão</h4>
              <p>Não foi possível conectar ao servidor. Tente novamente.</p>
              <button type="button" class="retry-btn" onclick="location.reload()">Tentar Novamente</button>
            </div>
          `;
        }
      };
    };

    // Função para formatar tamanho do arquivo
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Inicia automaticamente um novo chat
    startNewChat();
  });

  // Função global para fechar modal de documento
  window.closeDocumentModal = () => {
    const modal = document.querySelector('.document-upload-modal');
    if (modal) {
      document.body.removeChild(modal);
    }
    
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
      messageInput.focus();
    }
  };