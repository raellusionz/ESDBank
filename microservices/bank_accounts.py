from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from decimal import Decimal
import psycopg2
from datetime import datetime
import os

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

class bank_accounts(db.Model):
    __tablename__ = 'bank_acct_details_db'

    bank_acct_id = db.Column(db.String(20), primary_key=True)
    acct_balance = db.Column(db.DECIMAL(15,2), nullable=False)

    def __init__(self, bank_acct_id, acct_balance):
        self.bank_acct_id = bank_acct_id
        self.acct_balance = acct_balance


    def json(self):
        return {"bank_acct_id": self.bank_acct_id, "acct_balance": self.acct_balance}

@app.route("/")
def homepage():
    return "Welcome to the homepage of the bank_accounts microservice Lab4Proj."

@app.route("/bankAccounts")
def get_all():
    bank_accounts_list = db.session.scalars(db.select(bank_accounts)).all()

    if len(bank_accounts_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bank_accounts": [bank_account.json() for bank_account in bank_accounts_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no bank accounts."
        }
    ), 404

@app.route("/bankAccounts/bank_acct_id/<string:id_num>")
def find_by_bank_acct_id(id_num):
    account = db.session.scalars(
    	db.select(bank_accounts).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()


    if account:
        return jsonify(
            {
                "code": 200,
                "data": account.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404

# For now only handles float values
@app.route("/bankAccounts/add_amount/<string:id_num>/<float:amount>", methods=['PUT'])
def add_amount(id_num, amount):
    account = db.session.scalars(
    	db.select(bank_accounts).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()

    if account:
        amount = round(Decimal(amount), 2)
        account.acct_balance += amount
        transaction_time = datetime.now()  # Get the current time
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Amount added successfully.",
                "data": 
                    {
                        "timeOfTransaction": transaction_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "account": account.json()
                    }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404

# For now only handles float values
@app.route("/bankAccounts/deduct_amount/<string:id_num>/<float:amount>", methods=['PUT'])
def deduct_amount(id_num, amount):
    account = db.session.scalars(
    	db.select(bank_accounts).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()

    if account:
        amount = round(Decimal(amount), 2)
        
        # Error handling for bad request
        if amount > account.acct_balance:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Bad request. Not enough funds to deduct ${amount}.",
                    "data": account.json()
                }
            ), 400

        account.acct_balance -= amount
        transaction_time = datetime.now()  # Get the current time
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Amount deducted successfully.",
                "data": 
                    {
                        "timeOfTransaction": transaction_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "account": account.json()
                    }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404

# Third function for transaction between 2 accounts, should take 2 bank_acct_id and 1 amount
@app.route("/bankAccounts/transferral/<string:sender_acct_id>/<string:recipient_acct_id>/<float:amount>", methods=['PUT'])
def transferral(sender_acct_id, recipient_acct_id, amount):

    sender_account = db.session.scalars(
    	db.select(bank_accounts).filter_by(bank_acct_id=sender_acct_id).
    	limit(1)
        ).first()
    
    recipient_account = db.session.scalars(
    	db.select(bank_accounts).filter_by(bank_acct_id=recipient_acct_id).
    	limit(1)
        ).first()

    if sender_account:
        amount = round(Decimal(amount), 2)

        if amount > sender_account.acct_balance:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Bad request. Not enough funds to deduct ${amount}.",
                    "data": sender_account.json()
                }
            ), 400

        if recipient_account:
            sender_account.acct_balance -= amount
            recipient_account.acct_balance += amount
            transaction_time = datetime.now()  # Get the current time
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": "Transfer successful.",
                    "data": 
                        {   
                            "timeOfTransaction": transaction_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "sender": sender_account.json(),
                            "recipient": recipient_account.json(),
                            "amount": amount
                        }
                },
            )

        else:
            return jsonify(
                {
                    "code": 404,
                    "message": "Recipient bank account not found."
                }
            ), 404
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Sender bank account not found."
            }
        ), 404


if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to bank_accounts database ...")  
    app.run(host='0.0.0.0', port=5001, debug=True)