#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import requests
import json
from enum import Enum

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from mailersend import emails
from email_functions import sendEmail

app = Flask(__name__)
CORS(app)


@app.route("/notification/email", methods=['POST'])
def sendEmailNotification():
    # Check if the request contains valid JSON
    notificationDetails = None
    if request.is_json:
        notificationDetails = request.get_json()
        result = processNotificationDetails(notificationDetails)
        return result, result["code"]
    
    else:
        notificationDetails = request.get_data()
        print("Received an invalid details:")
        print(notificationDetails)
        print()
        return jsonify({"code": 400, "message": "Notification details input should be in JSON."}), 400 # Bad Request

def processNotificationDetails(details):
    print("Processing a notification details:")
    print(details)

    senderFullname = str(details["data"]["senderFullname"])
    senderEmail = str(details["data"]["senderEmail"])
    recipientFullname = str(details["data"]["recipientFullname"])
    recipientEmail = str(details["data"]["recipientEmail"])
    amount = str(details["data"]["amount"])
    transactionDate = str(details["data"]["transactionDate"])
    transactionID = str(details["data"]["transactionID"])
    senderContent = "Sent to"
    recipientContent = "Received from"
    print()  # print a new line feed as a separator

    try:
        sendEmail(senderFullname, recipientFullname, senderEmail, amount, transactionDate, transactionID, senderContent)
        sendEmail(recipientFullname, senderFullname, recipientEmail, amount, transactionDate, transactionID, recipientContent)

    except:
        return  {
                "code": 500,
                "message": "An error occurred sending the notification emails."
                }

    return  {
            "code": 201,
            "message": "Notification mails successfully sent."
            }


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("This is flask for " + os.path.basename(__file__) + ": sending notifications ...")
    app.run(host='0.0.0.0', port=5004, debug=True)


