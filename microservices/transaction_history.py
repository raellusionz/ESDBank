#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from os import environ
import psycopg2
from sqlalchemy import BigInteger, or_

app = Flask(__name__)

# Configure PostgreSQL database URI
POSTGRES_USER = "default"
POSTGRES_PASSWORD = "vHFyts8wa4PK"
POSTGRES_HOST = "ep-shiny-wave-a4w35od7-pooler.us-east-1.aws.neon.tech"
POSTGRES_DB = "verceldb"

# PostgreSQL URI format: postgresql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class transaction_logs(db.Model):
    __tablename__ = 'txn_hist_db'

    txn_id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    crban = db.Column(db.String(20), nullable=False)
    drban = db.Column(db.String(20), nullable=False) 
    txn_amt = db.Column(db.DECIMAL(15,2), nullable=False)
    txn_time = db.Column(db.String(100), nullable=False)

    def __init__(self, crban, drban, txn_amt, txn_time):
        self.crban = crban
        self.drban = drban
        self.txn_amt = txn_amt
        self.txn_time = txn_time

    def json(self):
        return {
            "txn_id": self.txn_id,
            "crban": self.crban,
            "drban": self.drban,
            "txn_amt": float(self.txn_amt),  # Convert Decimal to float for JSON serialization
            "txn_time": self.txn_time
        }

@app.route("/")
def homepage():
    return "Welcome to the homepage of the transaction_history microservice Lab4Proj."

@app.route("/transactionHistory")
def get_all():
    transaction_logs_list = db.session.scalars(db.select(transaction_logs)).all()

    if len(transaction_logs_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "transaction_history": [transaction_log.json() for transaction_log in transaction_logs_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no transaction history for any account."
        }
    ), 404

# find by creditor BAN - PROBLEM IS TXN HISTORY SEEMS TO TAKE BOTH DR AND CR SO CANNOT REALLY SEARCH BY BANK ACCOUNT
@app.route("/transactionHistory/bank_acct_id/<string:bank_acct_id>")
def find_by_bank_acct_id(bank_acct_id):
    logs = db.session.scalars(
    	db.select(transaction_logs).filter(or_(transaction_logs.crban == bank_acct_id, transaction_logs.drban == bank_acct_id))
        ).all()

    if logs:
        return jsonify(
            {
                "code": 200,
                "data": [log.json() for log in logs]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No transaction history for this user."
        }
    ), 404


@app.route("/transaction_history", methods=['POST'])
def insertTransactionLog():
    # Check if the transaction log contains valid JSON
    transaction_details = None
    if request.is_json:
        transaction_details = request.get_json()
        result = processTransactionDetails(transaction_details)
        return result, result["code"]
    else:
        data = request.get_data()
        print("Received invalid fund transferral details:")
        print(data)
        return jsonify({"code": 400,
                        # make the data string as we dunno what could be the actual format
                        "data": str(data),
                        "message": "Fund transferral details should be in JSON."}), 400  # Bad Request input


def processTransactionDetails(transaction_details):
    print("Processing fund transferral details:")
    print(transaction_details)
    timeOfTransaction = transaction_details["timeOfTransaction"]
    drBAN = transaction_details["sender"]["bank_acct_id"]
    crBAN = transaction_details["recipient"]["bank_acct_id"]
    transaction_amount = transaction_details["amount"]
    # If transaction id contains "ERROR", simulate failure

    print()  # print a new line feed as a separator

    transaction_log = transaction_logs(crBAN, drBAN, transaction_amount, timeOfTransaction)

    try:
        db.session.add(transaction_log)
        db.session.commit()
    except:
        return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the transaction."
                }


    return  {
            "code": 201,
            "message": "Transaction successfully logged.",
            "data": transaction_log.json(),
            }



# execute this program only if it is run as a script (not by 'import')
if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) +
          ": recording transaction history logs ...")  
    app.run(host='0.0.0.0', port=5003, debug=True)