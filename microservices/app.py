from flask import Flask, render_template, request, jsonify
import requests
import json
from invokes import invoke_http

RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'

app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/getTransactionHist", methods=['POST'])    
def getTransactionHist():
    bankID = request.json['bankID']
    transactionHist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankID), method='GET')
    return transactionHist

@app.route("/getAccountBalance", methods=['POST'])    
def getAccountBalance():
    bankID = request.json['bankID']
    accountBalance = invoke_http("http://127.0.0.1:5001/bankAccounts/bank_acct_id/" + str(bankID), method='GET')
    return accountBalance

@app.route("/roboadvisor")
def roboadvisor():
    return render_template("roboadvisor.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json['message']

    # Here, you could add logic to generate a response to the message
    rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that.'
    return jsonify({'response': bot_response })

@app.route("/transferFundsFromUI", methods=['POST'])    
def transferFundsFromUI():
    request_data = request.get_json()
    result = invoke_http("http://127.0.0.1:5100/transfer_funds", method='POST', json=request_data)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4999, debug=True)