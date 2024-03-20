// for testing purposes, these values should be retrieved from the session of the current user
bankID = 838853968388
fullname = "Jakob Lie WIe Yong"
email = "jakoblwr@gmail.com"
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
function submitForm() {

  // Fetch form data
  const phoneNumber= document.getElementById('phoneNumber').value;
  // transfer_funds can only handle floats
  const amount = parseFloat(document.getElementById('amount').value);
  const category = document.getElementById('category').value;
  const comments = document.getElementById('comments').value;

  // Prepare data for POST request
  const formData = {
      senderFullname: fullname, 
      senderBAN: bankID,
      senderEmail: email,
      recipientPhoneNumber: phoneNumber,
      transactionAmount: amount,
      category: category,
      comments: comments
  };

  // Make AJAX POST request to Flask app
  fetch('/transferFundsFromUI', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
  })
  .then(response => {
      if (response.ok) {
          // Handle success response
          alert('Transfer successful!');
          // Optionally, you can redirect the user to another page
          // window.location.href = '/success';
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
