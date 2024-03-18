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

class user_preference_logs(db.Model):
    __tablename__ = 'user_prefers_table'

    bank_acct_id = db.Column(db.String(20), primary_key=True)
    saving_goal_percent = db.Column(db.DECIMAL(15,2))
    necessity_expenditure_percent = db.Column(db.DECIMAL(15,2))

    def __init__(self, bank_acct_id, saving_goal_percent, necessity_expenditure_percent):
        self.bank_acct_id = bank_acct_id
        self.saving_goal_percent = saving_goal_percent
        self.necessity_expenditure_percent = necessity_expenditure_percent

    def json(self):
        return {
            "bank_acct_id": self.bank_acct_id, 
            "saving_goal_percent": self.saving_goal_percent,
            "necessity_expenditure_percent": self.necessity_expenditure_percent}

@app.route("/")
def homepage():
    return "Welcome to the homepage of the user_preference microservice Lab4Proj."


# Get the whole database

@app.route("/userPreference")
def get_all():
    user_preference_list = db.session.scalars(db.select(user_preference_logs)).all()

    if len(user_preference_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "User Preference": [user_preference.json() for user_preference in user_preference_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are No User Preference Available."
        }
    ), 404


#retreiving user saving goals percent

@app.route("/userPreference/user_saving_goal/<string:id_num>")
def get_saving_percent(id_num):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        saving_goal_percent = account.json()["saving_goal_percent"]
        return jsonify(    
            {
                "code": 200,
                "data": {
                    "saving_goal_percent": saving_goal_percent
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#retreiving user necessity expenditure percent

@app.route("/userPreference/user_expenditure/<string:id_num>")
def get_expenditure_percent(id_num):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        necessity_expenditure_percentage = account.json()["necessity_expenditure_percent"]
        return jsonify(    
            {
                "code": 200,
                "data": {
                    "expanditure_target_percent": necessity_expenditure_percentage
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#Updating user saving goals percent
@app.route("/userPreference/goal_perc_update/<string:id_num>/<float:saving_percent>",methods=['PUT'])
def update_saving_goal(id_num,saving_percent):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    
    if account:
        account.saving_goal_percent = saving_percent
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Saving Goal Target Updated Successfully.",
                "data": 
                    {
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


#Updating necessity expenditure percent
@app.route("/userPreference/expenditure_update/<string:id_num>/<float:expenditure_percent>",methods=['PUT'])
def update_expenditure_target(id_num,expenditure_percent):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        account.necessity_expenditure_percent = expenditure_percent
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Expenditure Target Updated Successfully.",
                "data": 
                    {
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


if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to bank_accounts database ...")  
    app.run(host='0.0.0.0', port=5006, debug=True)