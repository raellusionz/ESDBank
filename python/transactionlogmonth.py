from connectiondb import *
from flask import Flask, request, jsonify, render_template
import calendar

def get_month_name(month_number):
    return calendar.month_name[month_number]
accountnumber = "334455667788"
month = 2
month_name = get_month_name(month)
transactionmonthdata = transaction_log_month(accountnumber,month)
transactions_dict_month = []
for transaction in transactionmonthdata:
    # Assuming transaction is a tuple with specific fields, convert it to a dictionary
    transaction_dict = {
        "txn_id": transaction[0],  # Replace field1, field2, etc. with your actual field names
        "crban": transaction[1],
        "drban": transaction[2],
        "txn_amt": transaction[3],
        "txn_time": transaction[4],
    }
    transactions_dict_month.append(transaction_dict)

app = Flask(__name__ , template_folder='../client/view')

@app.route("/transactionmonthtesting")

def transaction_test(): 
    if len(transactionmonthdata) != 0:
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

@app.route("/transactionlogmonth")
def results():
    monthspendpos = 0
    monthspendneg = 0
    for txn in transactions_dict_month:
        if txn["crban"] == accountnumber:
            monthspendpos += txn["txn_amt"]
        if txn["drban"] == accountnumber:
            monthspendneg += txn["txn_amt"]

    context = {
        "title": "Transaction By Month",
        "transactionsByMonths": transactions_dict_month,
        "monthspendpos" : monthspendpos,
        "monthspendneg" : monthspendneg
    }
    return render_template("transactionlogmonth.html", **context)


if __name__ == '__main__':
    app.run(port=5000, debug=True)