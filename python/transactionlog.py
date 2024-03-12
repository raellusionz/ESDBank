from connectiondb import *
from transactionlogfunctions import *
from flask import Flask, request, jsonify, render_template

acct_number = "334455667788"
transactiondb = transaction_log(acct_number)
transactions_dict_full = transactionjsondata(transactiondb)
month = 2
month_name = get_month_name(month)
transactionmonthdata = transaction_log_month(acct_number,month)
transactions_dict_month = transactionjsondata(transactionmonthdata)
bank_balance = specific_bank_connection(acct_number)

app = Flask(__name__, template_folder='../client/view')

@app.route("/")
def results():
    calculated_results = monthlyspendcalc(acct_number,transactions_dict_month)
    title1 = "donkey"
    context = {
        "title": title1,
        "transactions_dict_full": transactions_dict_full,
        "transactionsByMonths": transactions_dict_month,
        "monthspendpos" : calculated_results[0],
        "monthspendneg" : calculated_results[1],
        "bank_balance" : bank_balance,
        "acct_number" : acct_number
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

@app.route("/transactionmonthtesting")

def transaction_test_month(): 
    if len(transactions_dict_month) != 0:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Transaction for " + month_name : transactions_dict_month
                    #[transaction.json() for transaction in transactions_dict_month]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no transactions available for the month of " + month_name + "."
        }
    ), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)