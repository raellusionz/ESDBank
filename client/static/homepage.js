// for testing purposes
bankID = 123456789012
currMonth = '02'

quickTransferForm = document.getElementById("quickTransfer")
quickTransferForm.addEventListener('submit', (event) => {
  console.log(quickTransferForm);
});

fetch('/getTransactionHist', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({bankID: bankID}),
})
.then(response => response.json())
.then(data => {
  transactions = data.data
  for (const transaction of transactions.slice(0, 6)) {
    if (transaction.crban == bankID) {
      document.getElementById("transactionDisplay").innerHTML += 
      `<tr>
        <td>${transaction.drban}</td>
        <td><span class='text-success'>${transaction.txn_amt}</span></td>
        <td>${transaction.txn_time}</td>
      </tr>`
    } else {
      document.getElementById("transactionDisplay").innerHTML += 
      `<tr>
        <td>${transaction.crban}</td>
        <td><span class='text-danger'>${transaction.txn_amt}</span></td>
        <td>${transaction.txn_time}</td>
      </tr>`
    }
  }
})
.catch((error) => {
  console.error('Error:', error);
});

fetch('/getAccountBalance', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({bankID: bankID}),
})
.then(response => response.json())
.then(data => {
  document.getElementById("accountBalance").innerText += data.data.acct_balance
})
.catch((error) => {
  console.error('Error:', error);
});