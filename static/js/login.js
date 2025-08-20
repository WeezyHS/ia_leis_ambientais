// Aguarda todo o conteúdo HTML da página ser carregado antes de executar o código
document.addEventListener('DOMContentLoaded', () => {
    
    // Encontra os elementos HTML com os quais vamos interagir
    const loginForm = document.getElementById('login-form');
    const errorMessageDiv = document.getElementById('error-message');

    // Adiciona um "ouvinte" que dispara uma função quando o formulário é submetido
    loginForm.addEventListener('submit', async (event) => {
        // Previne o comportamento padrão do formulário, que é recarregar a página
        event.preventDefault();

        // Limpa mensagens de erro antigas
        errorMessageDiv.textContent = '';

        // Pega os valores dos campos de email e senha
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // --- A PONTE PARA O BACKEND ---
        // Usa a função 'fetch' para enviar os dados para o nosso servidor FastAPI
        try {
            const response = await fetch('/login', {
                method: 'POST', // O método tem que ser POST, como definido no nosso @app.post('/login')
                headers: {
                    'Content-Type': 'application/json', // Informa ao servidor que estamos a enviar dados em formato JSON
                },
                body: JSON.stringify({ email: email, password: password }), // Converte os nossos dados para uma string JSON
            });

            // Pega a resposta JSON do servidor
            const data = await response.json();

            // Verifica se a resposta do servidor foi um erro (como o 401 que simulámos)
            if (!response.ok) {
                // Se falhou, mostra a mensagem de erro que o backend enviou
                errorMessageDiv.textContent = data.message || 'Ocorreu um erro.';
            } else {
                // LOGIN BEM-SUCEDIDO!
                // Agora, redirecionamos o usuário para a página de chat
                window.location.href = "/dashboard";
            }

        } catch (error) {
            // Se houver um erro de rede (ex: servidor desligado)
            errorMessageDiv.textContent = 'Não foi possível conectar ao servidor.';
            console.error('Erro de rede:', error);
        }
    });
});