from flask import Flask, render_template, request
import requests
import json
from invokes import invoke_http

app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/getTransactionHist", methods=['POST'])    
def getTransactionHist():
    bankID = request.json['bankID']
    transactionHist = invoke_http("/transactionHistory/bank_acct_id/" + str(bankID), method='GET')
    return transactionHist
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)