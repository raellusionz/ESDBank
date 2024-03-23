const main = Vue.createApp({
    // Data Properties
    data() {
        return {
        };
    },

    // Methods
    methods: {
        submit() {
            console.log("Query sent");
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
                botResponseDiv.textContent = `Finley: ${data.response}`;
                chatBox.appendChild(botResponseDiv);
                
                inputField.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }
        },
    },

    // Lifecycle Hook
    mounted() {
        const chatBox = document.getElementById('chat-box');
                
        const botResponseDiv = document.createElement('div');
        botResponseDiv.textContent = `Finley: Hello, I am Finley. Ask me anything!`;
        chatBox.appendChild(botResponseDiv);
    },
})

main.mount('#main');