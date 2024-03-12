from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

user_accounts_URL = "http://127.0.0.1:5000/userAccounts/hp_num/"
bank_accounts_URL = "http://127.0.0.1:5001/bankAccounts/transferral/"
activity_log_URL = "http://127.0.0.1:5002/activity_log"
transaction_history_URL = "http://127.0.0.1:5003/transaction_history"
notification_URL = "http://127.0.0.1:5004/notification/email"
error_URL = "http://127.0.0.1:5005/error"

@app.route("/transfer_funds", methods=['POST'])
def transfer_funds():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            details = request.get_json()
            print("\nReceived a fund transferral request in JSON:", details)

            # do the actual work
            # 1. Send transfer details from UI {SenderFullname, SenderBAN, SenderEmail, RecipientPhoneNumber, TransactionAmount}
            result = processTransferFunds(details)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "transfer_funds.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processTransferFunds(details):
    recipient_hp = details["recipientPhoneNumber"]
    senderBAN = details['senderBAN']
    transactionAmount = details['transactionAmount']

    # 2. Send the phone number {recipientPhoneNumber}
    # Invoke the user_accounts microservice
    print('\n-----Invoking user_accounts microservice-----')
    user_accounts_result = invoke_http(user_accounts_URL+f"{recipient_hp}", method='GET')
    print('user_accounts_result:', user_accounts_result)

    # 4. Record new user_accounts lookup activity
    print('\n\n-----Invoking activity_log microservice-----')
    invoke_http(activity_log_URL, method="POST", json=user_accounts_result)
    print("\nDatabase phone number lookup request sent to activity log.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails

    # Check the user_accounts lookup result; if a failure, send it to the error microservice.
    code = user_accounts_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Invoking error microservice as transfer fails-----')
        invoke_http(error_URL, method="POST", json=user_accounts_result)

        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("User_accounts MS status ({:d}) sent to the error microservice:".format(
            code), user_accounts_result)


        # 5. Return error
        return {
            "code": 500,
            "data": {"user_accounts_result": user_accounts_result},
            "message": "User_accounts lookup failure sent for error handling."
        }

    # 5. Send retrieved bank_acct_ids to bank_accounts microservice
    print('\n\n-----Invoking bank_accounts microservice-----')
    recipient_BAN = user_accounts_result["data"]["bank_acct_id"]
    bank_accounts_result = invoke_http(bank_accounts_URL+f"/{senderBAN}/{recipient_BAN}/{transactionAmount}", method="PUT")
    print('bank_accounts_result:', bank_accounts_result)


    # 7. Record new transferral activity
    print('\n\n-----Invoking activity_log microservice-----')
    invoke_http(activity_log_URL, method="POST", json=bank_accounts_result)
    print("\nTransfer request sent to activity log.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # Check the transfer request result; if a failure, send it to the error microservice.
    code = bank_accounts_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Invoking error microservice as transfer fails-----')
        invoke_http(error_URL, method="POST", json=bank_accounts_result)

        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("Bank_accounts MS status ({:d}) sent to the error microservice:".format(
            code), bank_accounts_result)


        # 7. Return error
        return {
            "code": 500,
            "data": {"bank_accounts_result": bank_accounts_result},
            "message": "Bank_accounts fund transferral failure sent for error handling."
        }

    # 8. Send new transfer request to transaction history
    # Invoke the transaction_history microservice
    print('\n\n-----Invoking transaction_history microservice-----')
    transaction_history_result = invoke_http(
        transaction_history_URL, method="POST", json=bank_accounts_result['data'])
    print("transaction_history_result:", transaction_history_result, '\n')

    # 9. Send the relevant info {senderFullname, recipientFullname, senderEmail, recipientEmail} to notification microservice
    # Invoke the notification microservice
    print('\n\n-----Invoking notification microservice-----')
    senderFullname = details["senderFullname"]
    senderEmail = details["senderEmail"]
    recipientFullname = user_accounts_result["data"]["user_fullname"]
    recipientEmail = user_accounts_result["data"]["user_email"]
    data = {
            "data": {
                "senderFullname": senderFullname,
                "senderEmail": senderEmail,
                "recipientFullname": recipientFullname,
                "recipientEmail": recipientEmail,
                "amount": transactionAmount
                }
            }
    notification_result = invoke_http(notification_URL, method="POST", json=data)
    print("notification result:", notification_result, '\n')

    # 10. Return successful fund transfer results
    return {
        "code": 201,
        "data": {
            "bank_accounts_result": bank_accounts_result,
            "transaction_history_result": transaction_history_result
        }

    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) +
          " for transferring funds...")
    app.run(host="0.0.0.0", port=5100, debug=True)