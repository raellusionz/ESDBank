document.getElementById('chat-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const inputField = document.getElementById('chat-input');
  const message = inputField.value.trim();
  if (message) {
    fetch('/webhook', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({message: message}),
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      const chatBox = document.getElementById('chat-box');
      const userMessageDiv = document.createElement('div');
      userMessageDiv.textContent = `You: ${message}`;
      chatBox.appendChild(userMessageDiv);
      
      const botResponseDiv = document.createElement('div');
      botResponseDiv.textContent = `Bot: ${data.response}`;
      chatBox.appendChild(botResponseDiv);
      
      inputField.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }
});