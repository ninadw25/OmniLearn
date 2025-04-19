// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const sessionIdInput = document.getElementById('sessionId');
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// State
let isUploading = false;
let isSending = false;

// Helper function to add messages to the chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    // Parse markdown only for assistant messages
    if (isUser) {
        messageDiv.textContent = content;
    } else {
        // Set innerHTML with parsed markdown
        messageDiv.innerHTML = marked.parse(content, {
            breaks: true,
            gfm: true,
            sanitize: true
        });

        // Apply syntax highlighting to code blocks
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            Prism.highlightElement(block);
        });
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Handle code blocks syntax highlighting if needed
    if (!isUser && messageDiv.querySelectorAll('pre code').length > 0) {
        // Optional: Add syntax highlighting using libraries like Prism.js or highlight.js
    }
}

// Upload files
uploadButton.addEventListener('click', async () => {
    const files = fileInput.files;
    if (files.length === 0) {
        uploadStatus.textContent = 'Please select files to upload';
        return;
    }

    const sessionId = sessionIdInput.value;
    if (!sessionId) {
        uploadStatus.textContent = 'Please enter a session ID';
        return;
    }

    isUploading = true;
    uploadButton.disabled = true;
    uploadStatus.textContent = 'Uploading files...';

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }
    formData.append('session_id', sessionId);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        uploadStatus.textContent = 'Files uploaded successfully!';
        fileInput.value = ''; // Clear file input
    } catch (error) {
        uploadStatus.textContent = `Error uploading files: ${error.message}`;
    } finally {
        isUploading = false;
        uploadButton.disabled = false;
    }
});

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

    // Add user message to chat
    addMessage(message, true);

    try {
        const response = await fetch('/api/chat', {
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

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const data = await response.json();
        
        // Add assistant's response to chat
        addMessage(data.answer);

        // Clear input
        messageInput.value = '';
    } catch (error) {
        addMessage(`Error: ${error.message}`);
    } finally {
        isSending = false;
        sendButton.disabled = false;
        messageInput.disabled = false;
    }
}

// Event listeners for sending messages
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Save API key to localStorage if user opts in
apiKeyInput.addEventListener('change', () => {
    if (confirm('Would you like to save the API key for this session? (Only for development)')) {
        localStorage.setItem('groq_api_key', apiKeyInput.value);
    }
});

// Load saved API key if it exists
window.addEventListener('load', () => {
    const savedApiKey = localStorage.getItem('groq_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }
});

// File drag and drop handling
const fileUploadArea = document.querySelector('.file-upload');

fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = '#2563eb';
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.style.borderColor = '#e5e7eb';
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = '#e5e7eb';
    fileInput.files = e.dataTransfer.files;
});

// Modified upload function
async function uploadFiles() {
    const files = fileInput.files;
    if (files.length === 0) {
        uploadStatus.textContent = 'Please select files to upload';
        return;
    }

    const sessionId = sessionIdInput.value;
    if (!sessionId) {
        uploadStatus.textContent = 'Please enter a session ID';
        return;
    }

    isUploading = true;
    uploadButton.disabled = true;
    uploadStatus.textContent = 'Uploading files...';

    const formData = new FormData();
    for (const file of files) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            uploadStatus.textContent = 'Only PDF files are allowed';
            isUploading = false;
            uploadButton.disabled = false;
            return;
        }
        formData.append('files', file);
    }
    formData.append('session_id', sessionId);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
        }

        const data = await response.json();
        uploadStatus.textContent = 'Files uploaded successfully!';
        fileInput.value = ''; // Clear file input
    } catch (error) {
        uploadStatus.textContent = `Error uploading files: ${error.message}`;
    } finally {
        isUploading = false;
        uploadButton.disabled = false;
    }
}

// Replace the click event listener
uploadButton.removeEventListener('click', uploadFiles);
uploadButton.addEventListener('click', uploadFiles);