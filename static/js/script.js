document.addEventListener('DOMContentLoaded', () => {
    const chatToggleButton = document.querySelector(".chat-toggle");
    const body = document.body;

    chatToggleButton.addEventListener("click", function() {
        body.classList.toggle("chat-open"); 
    });

    const chatContainer = document.querySelector('.chat-container');
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input');
    const sendButton = document.querySelector('.send-button');
    const chatToggle = document.querySelector('.chat-toggle');
    let isExpanded = true;
    const USE_DEMO_RESPONSE = false; 

    const startThinking = () => {
        const lastMessage = chatMessages.querySelector('.message:last-child');
        if (lastMessage) {
            lastMessage.classList.add('thinking');
        }
    };

    const stopThinking = () => {
        const thinkingMessage = chatMessages.querySelector('.thinking');
        if (thinkingMessage) {
            thinkingMessage.classList.remove('thinking');
        }
    };

    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    const createMessage = (text, isOutgoing = false) => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isOutgoing ? 'outgoing' : 'incoming'}`;
        
        if (!isOutgoing) {
            messageElement.innerHTML = `
                <div class="avatar">
                    <i class="fas fa-brain"></i>
                    <div class="thinking-indicator">
                        <div class="dot dot1"></div>
                        <div class="dot dot2"></div>
                        <div class="dot dot3"></div>
                    </div>
                </div>
            `;
        }
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;
        messageElement.appendChild(messageContent);
        
        return messageElement;
    };

    const processResponse = (message, incomingMessage) => {
        if (USE_DEMO_RESPONSE) {
            setTimeout(() => {
                stopThinking();
                const messageContent = incomingMessage.querySelector('.message-content');
                const demoResponses = [
                    "I understand your question. Let me help you with that.",
                    "Here's what I found based on your query.",
                    "That's an interesting point. Here's my perspective.",
                    "I can help you with that. Here's what you need to know."
                ];
                messageContent.textContent = demoResponses[Math.floor(Math.random() * demoResponses.length)];
            }, 2000);
        } else {
            fetch('/predict', {
                method: 'POST',
                body: JSON.stringify({ input: message }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                stopThinking();
                const messageContent = incomingMessage.querySelector('.message-content');
                const cleanedResponse = data.response.replace(/^salesman:\s*/i, '');
                messageContent.textContent = cleanedResponse;
            })
            .catch(error => {
                console.error('Error:', error);
                stopThinking();
                const messageContent = incomingMessage.querySelector('.message-content');
                messageContent.textContent = 'Sorry, there was an error processing your request.';
            });
        }
    };
    // Send message function
    const sendMessage = () => {
        const message = chatInput.value.trim();
        if (message) {
            const outgoingMessage = createMessage(message, true);
            chatMessages.appendChild(outgoingMessage);
            chatInput.value = '';
            chatInput.style.height = '48px';
            
            const incomingMessage = createMessage('', false);
            chatMessages.appendChild(incomingMessage);
            startThinking();
            processResponse(message, incomingMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Toggle chat expansion
    chatToggle.addEventListener('click', () => {
        isExpanded = !isExpanded;
    
        if (isExpanded) {
            chatContainer.style.transform = 'translateY(0)';
            chatToggle.innerHTML = '<i class="fas fa-chevron-down"></i>';
        } else {
            chatContainer.style.transform = 'translateY(calc(100% - 60px))';
            chatToggle.innerHTML = '<i class="fas fa-chevron-up"></i>';
        }
    });
    
});