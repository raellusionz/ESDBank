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
        session["bankID"] = userAccntDetails["data"]["bank_acct_id"]
        session["userFullname"] = userAccntDetails["data"]["user_fullname"]
        session["userPhoneNum"] = userAccntDetails["data"]["user_hp"]
        session["userEmail"] = userAccntDetails["data"]["user_email"]
        return redirect(url_for("home"))
    else:
        return render_template("login.html")
    
@app.route("/signout", methods=["GET"])
def signout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/home")
@app.route("/")
def home():
    if "bankID" in session:
        bankID = session["bankID"]
        transactionHist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankID), method='GET')
        # print(transactionHist)
        accountBalance = invoke_http("http://127.0.0.1:5001/bankAccounts/bank_acct_id/" + str(bankID), method='GET')
        content = {"transactionHist": transactionHist['data'], "accountBalance": accountBalance['data'], "bankID": bankID}
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
    bankID = session["bankID"]
    content = {"bankID": bankID}
    return render_template("roboadvisor.html", content=content)

@app.route("/splitpay")
def splitpay():
    bankID = session["bankID"]
    groups = invoke_http("http://127.0.0.1:5010/members/bank_acct_id/" + str(bankID), method='GET')
    content = {
                "bankID": bankID, 
                "groups": groups['data']['groups_member_is_in']
            }
    return render_template("splitpay.html", content=content)

@app.route("/splitpayCreateGrp", methods=['POST'])
def splitpayCreateGrp():
    request_data = request.get_json()
    # print(request_data, type(request_data))
    createGrpData = {
        'curr_user_ban' : session["bankID"],
        'curr_user_fullname': session['userFullname'],
        'curr_user_email':session['userEmail'],
        'curr_user_hp': session["userPhoneNum"],
        'group_name': request_data['newGroupName'],
        'phone_num_list': [int(phone_num) for phone_num in request_data['phoneNums']],
    }
    print(createGrpData)
    result = invoke_http("http://127.0.0.1:5200/create_group", method='POST', json=createGrpData)
    return f"create group success"

@app.route("/splitpay/group/<groupName>/<groupID>")
def splitpayGrp(groupName, groupID):
    bankID = session["bankID"]
    members = invoke_http("http://127.0.0.1:5010/members/group_id/" + str(groupID), method='GET')
    pendingRequests = invoke_http("http://127.0.0.1:5010/splitRequests/pendingRequests/user_details/"+ str(bankID) + "/" + str(session['userPhoneNum']) + "/" + str(groupID), method='GET')
    # print(pendingRequests, bankID, session['userPhoneNum'], groupID)
    if pendingRequests["code"] == 404:
        content = {
            "bankID": bankID,
            "groupName": groupName,
            "groupID": groupID,
            "pendingRequests": [],
            "members": members['data']['groups_members'],
        }

    else:
        content = {
                "bankID": bankID,
                "groupName": groupName,
                "groupID": groupID,
                "pendingRequests": pendingRequests['data']['pending_requests_to_user_by_id'],
                "members": members['data']['groups_members'],
            }
    return render_template("splitpayGrp.html", content=content)

@app.route("/startSplitPayFromUI", methods=['POST'])
def startSplitPayFromUI():
    request_data = request.get_json()
    splitPayData =  { 
        "currUserBAN": session["bankID"], 
        "currUserFullname": session['userFullname'], 
        "curUserPhoneNum": session["userPhoneNum"], 
        "currUserEmail": session['userEmail'], 
        "requestedAmount": request_data['requestedAmount'], 
        "groupID": request_data['groupID']
    }
    result = invoke_http("http://127.0.0.1:5300/split_payment", method='POST', json=splitPayData)
    return f"create group success"

@app.route("/handle_split_reply", methods=['POST'])
def handle_split_reply():
    request_data = request.get_json()
    details = {
        "payingUserFullname": session["userFullname"],
        "payingUserEmail": session["userEmail"],
        "payingUserBan": session["bankID"],
        "requesterUserPhoneNum": request_data['request']['requester_hp'],
        "request_id": request_data["requestId"],
        "amount_to_pay": request_data['request']['amount_to_pay'],
        "reply": request_data['replyStatus'],
    }
    result = invoke_http("http://127.0.0.1:5400/handle_split_reply", method="POST", json=details)
    return f"splitpay status updated"

@app.route('/webhook', methods=['POST'])
def webhook():
    bankID = session["bankID"]
    user_message = request.json['message']

    # Here, you could add logic to generate a response to the message
    print(bankID)
    payload = {
        "message": user_message,
        "metadata": {
            "bankID": str(bankID)  # Converting the integer to a string
        }
    }
    print(payload)
    rasa_response = requests.post(RASA_API_URL, json=payload)
    rasa_response_json = rasa_response.json()

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that.'
    return jsonify({'response': bot_response })

@app.route("/transferFundsFromUI", methods=['POST'])    
def transferFundsFromUI():
    request_data = request.get_json()
    # Add the 'senderBAN' key with its value to the request_data dictionary
    request_data['senderBAN'] = session["bankID"]
    request_data["senderFullname"] = session["userFullname"]
    request_data["senderEmail"] = session["userEmail"]
    result = invoke_http("http://127.0.0.1:5100/transfer_funds", method='POST', json=request_data)
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4999, debug=True)