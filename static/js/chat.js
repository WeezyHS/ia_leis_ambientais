document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesArea = document.getElementById('chat-messages');
    const newChatBtn = document.querySelector('.new-chat-btn');

    let conversationHistory = [];
    let currentConversationId = null;

    const addMessage = (role, content) => {
        conversationHistory.push({ role: role, content: content });

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

        messagesArea.scrollTop = messagesArea.scrollHeight;
    };

    const startNewChat = () => {
        conversationHistory = [];
        currentConversationId = null;
        messagesArea.innerHTML = '';
        addMessage('assistant', 'Olá! Como posso ajudar você hoje?');
    };

    newChatBtn.addEventListener('click', startNewChat);

    const handleSendMessage = async (event) => {
        event.preventDefault();
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        addMessage('user', userMessage);
        messageInput.value = '';

        try {
            const response = await fetch('/ask-ia', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    history: conversationHistory, 
                    conversation_id: currentConversationId // Envia o ID (que é 'null' no primeiro envio)
                }),
            });

            if (!response.ok) throw new Error('A resposta do servidor não foi OK');

            const data = await response.json();
            const aiResponse = data.response;

            // --- NOVO: Guardamos o ID da conversa que o backend nos devolve ---
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
            }

            addMessage('assistant', aiResponse);

        } catch (error) {
            console.error('Erro ao comunicar com a IA:', error);
            addMessage('assistant', 'Desculpe, ocorreu um erro ao tentar conectar-me à IA.');
        }
    };

    messageForm.addEventListener('submit', handleSendMessage);

    startNewChat();
});