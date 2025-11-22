// Handle form submission
document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userInput = document.getElementById('userInput');
    const query = userInput.value.trim();
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const chatMessages = document.getElementById('chatMessages');
    
    if (!query) {
        return;
    }
    
    // Disable input and show loading
    userInput.disabled = true;
    submitBtn.disabled = true;
    loadingSpinner.style.display = 'inline';
    submitBtn.querySelector('span:first-child').textContent = 'Processing...';
    
    // Add user message to chat
    addMessage(query, 'user');
    userInput.value = '';
    
    try {
        // Send request to backend
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response to chat
            addMessage(data.response, 'bot');
        } else {
            // Show error message
            addMessage(`Error: ${data.error}`, 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        submitBtn.disabled = false;
        loadingSpinner.style.display = 'none';
        submitBtn.querySelector('span:first-child').textContent = 'Send';
        userInput.focus();
    }
});

// Add message to chat
function addMessage(text, type) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format the message (preserve line breaks)
    const formattedText = formatMessage(text);
    contentDiv.innerHTML = formattedText;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message text (preserve line breaks and format)
function formatMessage(text) {
    // Replace newlines with <br>
    let formatted = text.replace(/\n/g, '<br>');
    
    // Format place names (lines that are just place names)
    const lines = formatted.split('<br>');
    const formattedLines = lines.map(line => {
        const trimmed = line.trim();
        // If line is short and doesn't contain punctuation, it might be a place name
        if (trimmed.length > 0 && trimmed.length < 50 && !trimmed.includes('.') && !trimmed.includes('?') && !trimmed.includes('!')) {
            return `<strong>${trimmed}</strong>`;
        }
        return trimmed;
    });
    
    return formattedLines.join('<br>');
}

// Allow Enter key to submit (but Shift+Enter for new line)
document.getElementById('userInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('queryForm').dispatchEvent(new Event('submit'));
    }
});

// Focus input on load
window.addEventListener('load', () => {
    document.getElementById('userInput').focus();
});

