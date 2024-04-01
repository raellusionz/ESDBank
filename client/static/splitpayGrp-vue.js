const main = Vue.createApp({
    delimiters: ['{[', ']}'],

    data() {
        return {
            members: ['Chi', 'Sophie', 'Sarah'],
            group: "Phuket Trip",
            selectedMembers: [],
            paymentDescription: '',
            totalAmount: null,
            requests : [{requester: "Sophie", amount: 10}, {requester: "Sarah", amount: 10}],
            pastPayments: [{sender: "Sophie", receiver:"Chi", amount: 10}, {sender: "Sarah", receiver:"Chi", amount: 10}]
        };
    },
    methods: {
        addPayment() {
            if (this.selectedMembers.length > 0 && this.totalAmount && this.paymentDescription) {
                // Calculate split amount (this is a simple split; you might want more complex logic)
                const splitAmount = this.totalAmount / this.selectedMembers.length;
                console.log(`Payment Description: ${this.paymentDescription}`);
                console.log(`Total Amount: ${this.totalAmount}`);
                console.log(`Split Among: ${this.selectedMembers.join(', ')}`);
                console.log(`Each Pays: ${splitAmount}`);

                // Here you would typically send this data to your backend or handle it accordingly

                // Reset form for next entry
                this.selectedMembers = [];
                this.paymentDescription = '';
                this.totalAmount = null;
                // Optionally close the modal here if you're controlling it programmatically
            } else {
                alert("Please fill in all fields and select at least one member.");
            }
        },
        accept() {

        },
        decline() {

        },
    }
});

main.mount('#main');