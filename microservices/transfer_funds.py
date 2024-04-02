from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)

user_accounts_URL = "http://127.0.0.1:5000/userAccounts/hp_num/"
bank_accounts_URL = "http://127.0.0.1:5001/bankAccounts/transferral/"
transaction_history_URL = "http://127.0.0.1:5002/transaction_history"

exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
exchangetype = amqp_connection.secrets['exchangetype'] #topic 

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

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
            print('\n------------------------')
            print('\nresult: ', result)
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
    category = details['category']

    # 2. Send the phone number {recipientPhoneNumber}
    # Invoke the user_accounts microservice
    print('\n-----Invoking user_accounts microservice-----')
    user_accounts_result = invoke_http(user_accounts_URL+f"{recipient_hp}", method='GET')
    print('user_accounts_result:', user_accounts_result)


    code = user_accounts_result["code"]
    message = json.dumps(user_accounts_result)


    if code not in range(200, 300):

        print('\n\n-----Publishing the (user_accounts lookup error) message with routing_key=user_accounts.error-----')
        channel.basic_publish(exchange=exchangename, routing_key="user_accounts.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)


        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("\nUser_accounts MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), user_accounts_result)


        # 5. Return error
        return {
            "code": 500,
            "data": {"user_accounts_result": user_accounts_result},
            "message": "User_accounts lookup failure sent for error handling."
        }
    
    else:
        # 4. Record new user_accounts lookup activity
        print('\n\n-----Publishing the (user_accounts lookup details) message with routing_key=user_accounts.details-----')        
        channel.basic_publish(exchange=exchangename, routing_key="user_accounts.details", 
            body=message)
        
    print("\nDatabase phone number lookup request published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 5. Send retrieved bank_acct_ids to bank_accounts microservice
    print('\n\n-----Invoking bank_accounts microservice-----')
    recipient_BAN = user_accounts_result["data"]["bank_acct_id"]
    bank_accounts_result = invoke_http(bank_accounts_URL+f"{senderBAN}/{recipient_BAN}/{transactionAmount}", method="PUT")
    print('bank_accounts_result:', bank_accounts_result)


    # Check the transfer request result; if a failure, send it to the error microservice.
    code = bank_accounts_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Publishing the (bank_accounts transfer error) message with routing_key=bank_accounts.error-----')
        message = json.dumps(bank_accounts_result)
        channel.basic_publish(exchange=exchangename, routing_key="bank_accounts.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nBank_accounts MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), bank_accounts_result)


        # 7. Return error
        return {
            "code": 400,
            "data": {"bank_accounts_result": bank_accounts_result},
            "message": "Bank_accounts fund transferral failure sent for error handling."
        }
    
    else:
        # 4. Record new order
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (bank_accounts transfer details) message with routing_key=bank_accounts.details-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        channel.basic_publish(exchange=exchangename, routing_key="bank_accounts.details", 
            body=message)
        
    print("\nTransfer request published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails

    # 8. Send new transfer request details to RabbitMQ
    print('\n\n-----Invoking transaction_history microservice-----')

    # Store bank_accounts_result['data'] as a variable
    json_data = bank_accounts_result['data']
    # Add category into the json_data dictionary
    json_data["category"] = category
    transaction_history_result = invoke_http(
        transaction_history_URL, method="POST", json=json_data)
    print("transaction_history_result:", transaction_history_result, '\n')

    # Check the transfer request result; if a failure, send it to the error microservice.
    code = transaction_history_result["code"]
    message = json.dumps(transaction_history_result)

    if code not in range(200, 300):

        print('\n\n-----Publishing the (bank_accounts transfer error) message with routing_key=transaction_history.error-----')
        message = json.dumps(transaction_history_result)
        channel.basic_publish(exchange=exchangename, routing_key="transaction_history.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nTransaction_history MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), bank_accounts_result)


        # 7. Return error
        return {
            "code": 400,
            "data": {"transaction_history_result": bank_accounts_result},
            "message": "Transaction_history transaction logging failure sent for error handling."
        }
    
    else:
        # 4. Record new order
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (transaction_history logging details) message with routing_key=transaction_history.details-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        channel.basic_publish(exchange=exchangename, routing_key="transaction_history.details", 
            body=message)
        
    print("\nTransaction history log published to RabbitMQ Exchange.\n")



    # 9. Send the relevant info {senderFullname, recipientFullname, senderEmail, recipientEmail} to notification microservice
    # Invoke the notification microservice
    print('\n\n-----Invoking notification microservice-----')

    senderFullname = details["senderFullname"]
    senderEmail = details["senderEmail"]
    recipientFullname = user_accounts_result["data"]["user_fullname"]
    recipientEmail = user_accounts_result["data"]["user_email"]
    transaction_date = transaction_history_result["data"]["txn_time"]
    transaction_id = transaction_history_result["data"]["txn_id"]
    data = {
            "data": {
                "senderFullname": senderFullname,
                "senderEmail": senderEmail,
                "recipientFullname": recipientFullname,
                "recipientEmail": recipientEmail,
                "amount": transactionAmount,
                "transactionDate": transaction_date,
                "transactionID": transaction_id
                },
            "notification_type": "transfer_funds"
            }
    
    message = json.dumps(data)
    print('\n\n-----Publishing the (notification details) message with routing_key=notification.details-----')
    channel.basic_publish(exchange=exchangename, routing_key="notification.details", 
            body=message)
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