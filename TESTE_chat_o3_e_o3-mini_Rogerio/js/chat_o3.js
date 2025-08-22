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

    // Inicia automaticamente um novo chat
    startNewChat();
  });