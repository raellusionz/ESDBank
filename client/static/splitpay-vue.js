const main = Vue.createApp({
    delimiters: ['{[', ']}'],
    // Data Properties
    data() {
        return {
            keyedPhoneNum: '',
            phoneNums: [],
            notValid: false,
        };
    },

    // Methods
    methods: {
        addPhoneNum() {
            // Check if the phone number has exactly 8 digits and consists only of digits
            if (this.keyedPhoneNum.length === 8 && /^\d+$/.test(this.keyedPhoneNum)) {
                this.phoneNums.push(this.keyedPhoneNum)
                this.keyedPhoneNum = ''
                this.notValid = false
            } else {
                this.notValid = true
                this.keyedPhoneNum = '';
            }
        },
        createGrp() {
            console.log(this.phoneNums);
            // Make AJAX POST request to Flask app
            fetch('/splitpayCreateGrp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.phoneNums)
            })
            .then(response => {
                if (response.ok) {
                    // Handle success response
                    console.log('Create group successful!');
                    // Optionally, you can redirect the user to another page
                    // window.location.href = '/success';
                } else {
                    // Handle error response
                    alert('Error occurred during creating group.');
                    console.log("Error occurred during creating group1");
                    this.phoneNums = []
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error occurred during creating group.');
                console.log("Error occurred during creating group1");
            });
        },
    },

    // Computed Properties
    computed: {
    },

    // Lifecycle Hook
    mounted() {
    },
})

main.mount('#main');