// /static/js/chat.js
document.addEventListener('DOMContentLoaded', () => {
    const messageForm   = document.getElementById('message-form');
    const messageInput  = document.getElementById('message-input');
    const messagesArea  = document.getElementById('chat-messages');
    const newChatBtn    = document.querySelector('.new-chat-btn');
    const chatList      = document.getElementById('chat-list');
  
    // Memória em runtime (some ao recarregar a página).
    // Se quiser persistir entre recargas, dá pra trocar para localStorage.
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
      avatar.textContent = role === 'user' ? '👤' : '🤖';
  
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
      const a  = document.createElement('a');
      a.href = '#';
      a.textContent = title || 'Novo chat';
      
      // Criar ícone de lixeira
      const deleteIcon = document.createElement('span');
      deleteIcon.className = 'delete-chat-icon';
      deleteIcon.innerHTML = '🗑️';
      deleteIcon.title = 'Excluir chat';
      
      // Adicionar evento de clique no ícone para excluir chat
      deleteIcon.addEventListener('click', async (e) => {
        e.stopPropagation(); // Evita que o clique ative o chat
        e.preventDefault();
        
        // Confirmar exclusão
        if (!confirm('Tem certeza que deseja excluir este chat? Esta ação não pode ser desfeita.')) {
          return;
        }
        
        const conv = conversations.get(key);
        if (!conv || !li.dataset.id) {
          // Se não tem ID do backend, apenas remove da memória e UI
          conversations.delete(key);
          li.remove();
          if (currentConversationKey === key) {
            currentConversationKey = null;
            clearMessagesUI();
          }
          return;
        }
        
        try {
          // Chama o endpoint DELETE
          const response = await fetch(`/chat/${li.dataset.id}`, {
            method: 'DELETE'
          });
          
          if (response.ok) {
            // Remove da memória e da UI
            conversations.delete(key);
            li.remove();
            
            // Se era o chat ativo, limpa a área de mensagens
            if (currentConversationKey === key) {
              currentConversationKey = null;
              clearMessagesUI();
            }
          } else {
            alert('Erro ao excluir chat. Tente novamente.');
          }
        } catch (error) {
          console.error('Erro ao excluir chat:', error);
          alert('Erro ao excluir chat. Tente novamente.');
        }
      });
      
      li.appendChild(a);
      li.appendChild(deleteIcon);

      // Atribuímos o identificador "chave corrente" ao <li>
      // data-key: chave local (temp ou definitiva)
      // data-id:  id do backend (UUID), quando existir
      li.dataset.key = key;
      if (backendId) li.dataset.id = backendId;
  
      // Clique para abrir o chat
      li.addEventListener('click', async (e) => {
        e.preventDefault();
        const clickedKey = li.dataset.key;
        const conv = conversations.get(clickedKey);
        if (!conv) return;
  
        currentConversationKey = clickedKey;
        setActiveListItem(li);
  
        // Se você tiver endpoint para buscar histórico no backend,
        // descomente e ajuste:
        //
        // if (li.dataset.id) {
        //   const resp = await fetch(`/conversations/${li.dataset.id}`);
        //   const data = await resp.json();
        //   conv.messages = data.messages; // [{role, content}, ...]
        // }

        renderMessages(conv.messages);
      });

      chatList.prepend(li); // novo chat vai para o topo
      setActiveListItem(li);
      return li;
    };
  
    const updateListItemTitle = (key, title) => {
      const li = chatList.querySelector(`li[data-key="${CSS.escape(key)}"]`);
      if (li) {
        li.querySelector('a').textContent = title;
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
  
    // Fluxo de “Novo Chat”
    const startNewChat = () => {
      // cria uma chave temporária até o backend devolver o UUID
      const tempKey = uid();
  
      // cria o registro em memória
      conversations.set(tempKey, {
        id: null,
        title: 'Novo chat',
        messages: [{ role: 'assistant', content: 'Olá! Como posso ajudar você hoje?' }]
      });
  
      // cria o item na lista
      createListItem('Novo chat', tempKey, null);
  
      // zera a área e mostra a mensagem inicial
      currentConversationKey = tempKey;
      renderMessages(conversations.get(tempKey).messages);
    };
  
    newChatBtn.addEventListener('click', startNewChat);
  
    // Envio de mensagem
    const handleSendMessage = async (event) => {
      event.preventDefault();
      const userMessage = messageInput.value.trim();
      if (!userMessage) return;
  
      // Garante que exista uma conversa ativa (se recarregou a página sem clicar em “Novo Chat”)
      if (!currentConversationKey) {
        startNewChat();
      }
  
      // Atualiza memória + UI
      const conv = conversations.get(currentConversationKey);
      conv.messages.push({ role: 'user', content: userMessage });
      addMessageToUI('user', userMessage);
      messageInput.value = '';
  
      // (Opcional) atualiza título com as primeiras palavras da 1ª mensagem do usuário
      if (conv.title === 'Novo chat') {
        const short = userMessage.length > 28 ? userMessage.slice(0, 28) + '…' : userMessage;
        updateListItemTitle(currentConversationKey, short || 'Novo chat');
      }
  
      try {
        // Envia pro backend
        const body = {
          history: conv.messages,                     // [{role, content}]
          conversation_id: conv.id ?? null            // null na primeira mensagem desse chat
        };
  
        const response = await fetch('/ask-ia', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
  
        if (!response.ok) throw new Error('A resposta do servidor não foi OK');
  
        const data = await response.json();
        const aiResponse = data.response;
  
        // Se for a primeira resposta desta conversa, backend devolve o UUID
        if (data.conversation_id && !conv.id) {
          conv.id = data.conversation_id;
          attachBackendIdToItem(currentConversationKey, data.conversation_id);
        }
  
        // Atualiza memória + UI com a resposta
        conv.messages.push({ role: 'assistant', content: aiResponse });
        addMessageToUI('assistant', aiResponse);
  
      } catch (error) {
        console.error('Erro ao comunicar com a IA:', error);
        conv.messages.push({ role: 'assistant', content: 'Desculpe, ocorreu um erro ao tentar conectar-me à IA.' });
        addMessageToUI('assistant', 'Desculpe, ocorreu um erro ao tentar conectar-me à IA.');
      }
    };
  
    messageForm.addEventListener('submit', handleSendMessage);

    // Adiciona evento para enviar mensagem com Enter
    messageInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage(event);
      }
    });

    // Inicia com um chat vazio (estilo ChatGPT)
    startNewChat();
  });
  