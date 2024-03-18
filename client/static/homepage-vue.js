const main = Vue.createApp({
  delimiters: ['{[', ']}'],
  // Data Properties
  data() {
      return {
          transactions: {},
          month: 0,
          month_names: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          accountBalance: "",
          balanceChange: 0,
          moneyIn: 0,
          moneyOut: 0,
          bankID: "123456789012",
          form: {
            receiver: "",
            amount: "",
            category: "",
          }
      };
  },

  // Methods
  methods: {
    submit() {
      console.log(this.form);
    }
  },

  // Lifecycle Hook
  mounted() {
    date = new Date()
    this.month = date.getMonth()

    fetch('/getTransactionHist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({bankID: this.bankID}),
    })
    .then(response => response.json())
    .then(data => {
      transactions = data.data
      this.transactions = transactions.slice(0,8)
      // console.log(this.transactions);
      for (const transaction of transactions) {
        console.log(transaction);
        txnDate = new Date(transaction.txn_time)
        txnMonth = txnDate.getMonth();
        if (txnMonth == this.month) {
          if (transaction.crban == this.bankID) {
            this.moneyIn += transaction.txn_amt

          } else {
            this.moneyOut -= transaction.txn_amt

          }
        }
      }
      this.balanceChange = this.moneyIn - this.moneyOut
    })
    .catch((error) => {
      console.error('Error:', error);
    });
    
    fetch('/getAccountBalance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({bankID: this.bankID}),
    })
    .then(response => response.json())
    .then(data => {
      this.accountBalance = data.data.acct_balance
      // console.log(this.accountBalance);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  },
})

main.mount('#main');