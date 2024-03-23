from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
from invokes import invoke_http

RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'

app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")
app.secret_key = "esdSecret"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.json["email"]
        data = invoke_http("http://127.0.0.1:5000/userAccounts/user_email/" + email)
        data = json.dumps(data)
        userAccntDetails = json.loads(data)
        bankID = userAccntDetails["data"]["bank_acct_id"]
        session["bankID"] = bankID
        return redirect(url_for("home"))
    else:
        return render_template("login.html")

@app.route("/home")
@app.route("/")
def home():
    if "bankID" in session:
        bankID = session["bankID"]
        transactionHist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankID), method='GET')
        accountBalance = invoke_http("http://127.0.0.1:5001/bankAccounts/bank_acct_id/" + str(bankID), method='GET')
        content = {"transactionHist": transactionHist['data'], "accountBalance": accountBalance['data']}
        return render_template("homepage.html", content=content)
    else:
        print("redirecting to login again")
        return redirect(url_for("login"))

@app.route("/getTransactionHist")    
def getTransactionHist():
    bankID = session["bankID"]
    transactionHist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankID), method='GET')
    return transactionHist

@app.route("/roboadvisor")
def roboadvisor():
    return render_template("roboadvisor.html")

@app.route("/splitpay")
def splitpay():
    return render_template("splitpay.html")

@app.route("/splitpay/group")
def splitpayGrp():
    return render_template("splitpayGrp.html")

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
    # Add the 'senderBAN' key with its value to the request_data dictionary
    request_data['senderBAN'] = session["bankID"]
    result = invoke_http("http://127.0.0.1:5100/transfer_funds", method='POST', json=request_data)
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4999, debug=True)