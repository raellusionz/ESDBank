const main = Vue.createApp({
    delimiters: ['{[', ']}'],
    // Data Properties
    data() {
        return {
            keyedPhoneNum: '',
            groupName: '',
            phoneNums: [],
            notValid: false,
            groups: ['Phuket Trip', 'Japan Trip']
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
            console.log({'phoneNums': this.phoneNums,'groupName': this.groupName});
            // Make AJAX POST request to Flask app
            fetch('/splitpayCreateGrp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'phoneNums': this.phoneNums,'groupName': this.groupName})
            })
            .then(response => {
                if (response.ok) {
                    // Handle success response
                    console.log('Create group successful!');
                    this.phoneNums = [];
                    this.groupName = '';
                    // Optionally, you can redirect the user to another page
                    // window.location.href = '/success';
                } else {
                    // Handle error response
                    alert('Error occurred during creating group.');
                    console.log("Error occurred during creating group1");
                    this.phoneNums = [];
                    this.groupName = '';
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