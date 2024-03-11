from connectiondb import *
from flask import Flask, request, jsonify, render_template

acct_number = "334455667788"
transactiondb = transaction_log(acct_number)
transactions_dict_full = []
for transaction in transactiondb:
    # Assuming transaction is a tuple with specific fields, convert it to a dictionary
    transaction_dict = {
        "txn_id": transaction[0],  # Replace field1, field2, etc. with your actual field names
        "crban": transaction[1],
        "drban": transaction[2],
        "txn_amt": transaction[3],
        "txn_time": transaction[4],
    }
    transactions_dict_full.append(transaction_dict)

app = Flask(__name__, template_folder='../client/view')

@app.route("/")
def results():
    title1 = "donkey"
    context = {
        "title": title1,
        "transactions_dict_full": transactions_dict_full
    }
    return render_template("homepage.html", **context)


@app.route("/transactiontesting")

def transaction_test(): 
    if len(transactiondb) != 0:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Transaction for " + acct_number : transactions_dict_full
                    #[transaction.json() for transaction in transactions_dict_month]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no transactions available for " + acct_number + "."
        }
    ), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)