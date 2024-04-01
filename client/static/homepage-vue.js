const main = Vue.createApp({
  delimiters: ['{[', ']}'],
  // Data Properties
  data() {
      return {
          transactions: {},
          month: 0,
          month_names: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          balanceChange: 0,
          moneyIn: 0,
          moneyOut: 0,
          // bankID: "123456789012",
          form: {
            recipientPhoneNumber: "",
            transactionAmount: "",
            category: "",
          }
      };
  },

  // Methods
  methods: {
    submit() {
      // Make AJAX POST request to Flask app
      fetch('/transferFundsFromUI', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.form)
      })
      .then(response => {
          if (response.ok) {
              // Handle success response
              alert('Transfer successful!');
          } else {
              // Handle error response
              alert('Error occurred during transfer1.');
          }
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Error occurred during transfer2.');
      });
    }
  },

  // Lifecycle Hook
  mounted() {
    date = new Date()
    this.month = date.getMonth()

    fetch('/getTransactionHist', {
      method: 'GET', // Changed from 'POST' to 'GET'
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      let transactions = data.data;
      this.transactions = transactions.slice(0,8);
      for (const transaction of transactions) {
        let txnDate = new Date(transaction.txn_time);
        let txnMonth = txnDate.getMonth();
        if (txnMonth == this.month) {
          if (transaction.crban == this.bankID) {
            this.moneyIn += transaction.txn_amt;
          } else {
            this.moneyOut -= transaction.txn_amt;
          }
        }
      }
      this.balanceChange = this.moneyIn - this.moneyOut;
    })
    .catch((error) => {
      console.error('Error:', error);
    });    
  },
})

main.mount('#main');