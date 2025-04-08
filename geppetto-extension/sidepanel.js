document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('api-key');
  const saveKeyButton = document.getElementById('save-key');
  const apiKeyContainer = document.getElementById('api-key-container');
  const chatContainer = document.getElementById('chat-container');
  const messagesContainer = document.getElementById('messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');
  const aiProviderSelect = document.getElementById('ai-provider');
  const includePageContent = document.getElementById('include-page-content');

  let currentProvider = 'openai';

  // Check if API key is already saved
  chrome.storage.local.get(['api_key', 'ai_provider'], (result) => {
    if (result.api_key) {
      apiKeyInput.value = result.api_key;
      if (result.ai_provider) {
        aiProviderSelect.value = result.ai_provider;
        currentProvider = result.ai_provider;
      }
      showChatInterface();
    }
  });

  // Handle AI provider change
  aiProviderSelect.addEventListener('change', (e) => {
    currentProvider = e.target.value;
    chrome.storage.local.set({ ai_provider: currentProvider });
    // Clear the API key when switching providers
    apiKeyInput.value = '';
    chrome.storage.local.remove('api_key');
    showApiKeyInterface();
  });

  // Save API key
  saveKeyButton.addEventListener('click', () => {
    const apiKey = apiKeyInput.value.trim();
    if (apiKey) {
      chrome.storage.local.set({
        api_key: apiKey,
        ai_provider: currentProvider
      }, () => {
        showChatInterface();
      });
    } else {
      alert('Please enter a valid API key');
    }
  });

  // Show chat interface and hide API key input
  function showChatInterface() {
    apiKeyContainer.classList.add('hidden');
    chatContainer.classList.remove('hidden');
  }

  // Show API key interface and hide chat
  function showApiKeyInterface() {
    apiKeyContainer.classList.remove('hidden');
    chatContainer.classList.add('hidden');
  }

  // Handle sending messages
  sendButton.addEventListener('click', sendMessage);
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    // Add user message to chat
    addMessageToChat('user', userMessage);
    userInput.value = '';

    const thinkingId = addThinkingIndicator();

    try {
      let finalMessage = userMessage;

      // If page content is enabled, get the content from the active tab
      if (includePageContent.checked) {
        try {
          const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
          const pageContent = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => {
              return document.body.innerText;
            }
          });

          finalMessage = `Context from current page:\n${pageContent[0].result}\n\nUser query:\n${userMessage}`;

          // Auto-disable the toggle after use
          includePageContent.checked = false;
        } catch (error) {
          console.error('Error getting page content:', error);
          addMessageToChat('system', 'Failed to get page content. Proceeding with just the query...');
        }
      }

      const response = await callAI(finalMessage);
      removeThinkingIndicator(thinkingId);
      addMessageToChat('assistant', response);
    } catch (error) {
      removeThinkingIndicator(thinkingId);
      addMessageToChat('assistant', `Error: ${error.message}`);
    }
  }

  function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'assistant-message');

    // Process markdown-like syntax for code
    const formattedContent = content.replace(/`([^`]+)`/g, '<code>$1</code>')
                                  .replace(/\n/g, '<br>');

    messageDiv.innerHTML = formattedContent;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function addThinkingIndicator() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.classList.add('message', 'assistant-message', 'thinking');
    thinkingDiv.textContent = 'Thinking...';
    messagesContainer.appendChild(thinkingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return thinkingDiv.id = 'thinking-' + Date.now();
  }

  function removeThinkingIndicator(id) {
    const thinkingDiv = document.getElementById(id);
    if (thinkingDiv) {
      thinkingDiv.remove();
    }
  }

  async function callAI(message) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(['api_key'], async (result) => {
        if (!result.api_key) {
          reject(new Error('API key not found. Please set your API key.'));
          return;
        }

        try {
          let response;

          switch (currentProvider) {
            case 'openai':
              response = await callOpenAI(message, result.api_key);
              break;
            case 'anthropic':
              response = await callClaude(message, result.api_key);
              break;
            case 'gemini':
              response = await callGemini(message, result.api_key);
              break;
            default:
              throw new Error('Unknown AI provider');
          }

          resolve(response);
        } catch (error) {
          reject(error);
        }
      });
    });
  }

  async function callOpenAI(message, apiKey) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: 'You are a helpful AI assistant.' },
          { role: 'user', content: message }
        ],
        max_tokens: 1000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'OpenAI API error');
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async function callClaude(message, apiKey) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20240620',
        max_tokens: 1000,
        messages: [
          { role: 'user', content: message }
        ]
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Claude API error');
    }

    const data = await response.json();
    return data.content[0].text;
  }

  async function callGemini(message, apiKey) {
    const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': apiKey
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: message
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 1000,
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Gemini API error');
    }

    const data = await response.json();
    return data.candidates[0].content.parts[0].text;
  }
});