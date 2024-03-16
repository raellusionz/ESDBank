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
  console.log(data)
})
.catch((error) => {
  console.error('Error:', error);
});