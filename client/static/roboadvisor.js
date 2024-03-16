document.getElementById('chat-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const inputField = document.getElementById('chat-input');
    const message = inputField.value.trim();
    if (message) {
      const chatBox = document.getElementById('chat-box');
      const newMessageDiv = document.createElement('div');
      newMessageDiv.innerHTML = `<h5>User</h5>` + message;
      chatBox.appendChild(newMessageDiv);
      inputField.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  });
  