// for testing purposes
bankID = 123456789012

fetch('/getTransactionHist', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({bankID: bankID}),
})
.then(response => response.json())
.then(data => {
  for (const transaction of data.data.slice(0, 6)) {
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