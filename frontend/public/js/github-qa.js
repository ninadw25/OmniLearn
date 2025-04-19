// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const sessionIdInput = document.getElementById('sessionId');
const repoUrlInput = document.getElementById('repoUrl');
const processButton = document.getElementById('processButton');
const processStatus = document.getElementById('processStatus');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// State
let isProcessing = false;
let isSending = false;

// Helper function to add messages to the chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    if (isUser) {
        messageDiv.textContent = content;
    } else {
        messageDiv.innerHTML = marked.parse(content, {
            breaks: true,
            gfm: true,
            sanitize: true
        });

        messageDiv.querySelectorAll('pre code').forEach((block) => {
            Prism.highlightElement(block);
        });
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Process repository
async function processRepository() {
    const repoUrl = repoUrlInput.value.trim();
    const sessionId = sessionIdInput.value;

    if (!repoUrl || !sessionId) {
        processStatus.textContent = 'Please fill in all required fields';
        return;
    }

    isProcessing = true;
    processButton.disabled = true;
    processStatus.textContent = 'Processing repository...';

    try {
        console.log('Sending request to process repository:', {
            url: repoUrl,
            session_id: sessionId
        });

        // Use the correct backend URL
        const response = await fetch('http://localhost:8000/api/github/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: repoUrl,
                session_id: sessionId
            }),
        });

        // Get the response text first
        const responseText = await response.text();
        console.log('Raw server response:', responseText);

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            console.error('Failed to parse JSON response:', e);
            throw new Error(`Invalid JSON response: ${responseText}`);
        }

        if (!response.ok) {
            throw new Error(data.detail || `Server error (${response.status}): ${data.detail || 'Unknown error'}`);
        }

        processStatus.textContent = 'Repository processed successfully!';
        addMessage('Repository processed successfully! You can now ask questions about the code.', false);
    } catch (error) {
        const errorDetail = error.response?.data?.detail || error.message;
        processStatus.textContent = `Error processing repository: ${errorDetail}`;
        console.error('Repository processing error:', {
            error,
            status: error.response?.status,
            detail: error.response?.data?.detail,
            message: error.message,
            stack: error.stack
        });
    } finally {
        isProcessing = false;
        processButton.disabled = false;
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    const sessionId = sessionIdInput.value;
    const apiKey = apiKeyInput.value;

    if (!message || !sessionId || !apiKey) {
        alert('Please fill in all required fields');
        return;
    }

    if (isSending) return;

    isSending = true;
    sendButton.disabled = true;
    messageInput.disabled = true;

    addMessage(message, true);

    try {
        // Use the correct API endpoint URL
        const response = await fetch('http://localhost:8000/api/github/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                groq_api_key: apiKey,
            }),
        });

        // Log the response for debugging
        console.log('Chat response status:', response.status);
        const responseText = await response.text();
        console.log('Raw chat response:', responseText);

        if (!response.ok) {
            throw new Error(`Server error (${response.status}): ${responseText}`);
        }

        const data = JSON.parse(responseText);
        addMessage(data.answer);
        messageInput.value = '';
    } catch (error) {
        console.error('Chat error:', error);
        addMessage(`Error: ${error.message}`);
    } finally {
        isSending = false;
        sendButton.disabled = false;
        messageInput.disabled = false;
    }
}

// Event listeners
processButton.addEventListener('click', processRepository);
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Save API key to localStorage
apiKeyInput.addEventListener('change', () => {
    if (confirm('Would you like to save the API key for this session? (Only for development)')) {
        localStorage.setItem('groq_api_key', apiKeyInput.value);
    }
});

// Load saved API key
window.addEventListener('load', () => {
    const savedApiKey = localStorage.getItem('groq_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }
});