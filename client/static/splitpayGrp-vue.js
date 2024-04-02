const main = Vue.createApp({
    delimiters: ['{[', ']}'],

    data() {
        return {
            groupId: null,
            paymentDescription: '',
            totalAmount: null,
        };
    },
    methods: {
        addPayment() {
            console.log(this.totalAmount, this.groupId);
            // Make AJAX POST request to Flask app
            fetch('/startSplitPayFromUI', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"requestedAmount": this.totalAmount, "groupID": this.groupId})
            })
            .then(response => {
                if (response.ok) {
                    // Handle success response
                    alert('Request successful!');
                } else {
                    // Handle error response
                    alert('Error occurred during addPayment1.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error occurred during addPayment2.');
            });
        },

        handle_split_reply(reply, requestId, request) {
            fetch('/handle_split_reply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"replyStatus": reply, "requestId": requestId, "request": request})
            })
            .then(response => {
                if (response.ok) {
                    // Handle success response
                    alert('Request successful!');
                } else {
                    // Handle error response
                    alert('Error occurred during addPayment1.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error occurred during addPayment2.');
            });
        },

        accept(requestId, request) {
            this.handle_split_reply("accept", requestId, request)
        },
        decline(requestId, request) {
            this.handle_split_reply("decline", requestId, request)
        },
    },

    mounted() {
        this.groupId = document.getElementById('groupId').value;
    },
});

main.mount('#main');