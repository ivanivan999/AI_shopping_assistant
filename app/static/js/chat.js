// app/static/js/chat.js

let loadingMessageId = null;

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    const sendButton = document.getElementById('send-button');
    input.disabled = true;
    sendButton.disabled = true;

    addMessageToChat('user', message);
    input.value = '';

    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            user_id: 'USER001'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            data.messages.forEach(msg => {
                if (msg.role === 'tool') {
                    try {
                        const parsed = JSON.parse(msg.content);
                        const formatted = formatToolResponse(parsed);
                        addMessageToChat('assistant', formatted);
                    } catch (e) {
                        console.log('Tool message parse error:', e);
                    }
                } else if (msg.role === 'assistant') {
                    addMessageToChat('assistant', msg.content);
                }
            });
        } else {
            addMessageToChat('error', data.message || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessageToChat('error', 'Failed to get response');
    })
    .finally(() => {
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
    });
}

function addMessageToChat(role, content) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role} p-2 mb-2 rounded`;
    
    if (role === 'user') {
        messageDiv.classList.add('text-white', 'bg-primary', 'ml-auto');
        messageDiv.style.maxWidth = '75%';
        messageDiv.style.marginLeft = 'auto';
    } else {
        messageDiv.classList.add('bg-light');
        messageDiv.style.maxWidth = '75%';
    }
    
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function formatToolResponse(data) {
    if (Array.isArray(data)) {
        return data.map(item => `
            Product: ${item.name}
            Description: ${item.description}
            Price: $${item.price}
            Stock: ${item.inventory} units available
        `).join('\n\n');
    }
    return JSON.stringify(data, null, 2);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('user-input');
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});