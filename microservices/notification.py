from dotenv import dotenv_values
import requests
import json
from enum import Enum

#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMAIL_API="113EBD6868E6E19E40E314E7D80178CDA8D4FC01FBCC423ABD0A3EE039C03E4E4D0C2348B5E7B713F3B30B93482EB80F"

class ApiClient:
 apiUri = 'https://api.elasticemail.com/v2'
 secrets = dotenv_values(".env.development.local")
 apiKey = secrets["EMAIL_API"]

 def Request(method, url, data):
  data['apikey'] = ApiClient.apiKey
  if method == 'POST':
   result = requests.post(ApiClient.apiUri + url, data = data)
  elif method == 'PUT':
   result = requests.put(ApiClient.apiUri + url, data = data)
  elif method == 'GET':
   attach = ''
   for key in data:
    attach = attach + key + '=' + data[key] + '&' 
   url = url + '?' + attach[:-1]
   result = requests.get(ApiClient.apiUri + url) 
   
  jsonMy = result.json()
  
  if jsonMy['success'] is False:
   return jsonMy['error']
   
  return jsonMy['data']

def Send(subject, EEfrom, fromName, to, bodyHtml, bodyText, isTransactional):
 return ApiClient.Request('POST', '/email/send', {
  'subject': subject,
  'from': EEfrom,
  'fromName': fromName,
  'to': to,
  'bodyHtml': bodyHtml,
  'bodyText': bodyText,
  'isTransactional': isTransactional})

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
    print()  # print a new line feed as a separator

    try:
        Send("TEST", "esdbanknotification@gmail.com", "ESDBank", senderEmail, "<h1>This is a test<br> "+senderFullname+" "+amount+"</h1>", "This is a test", True)
        Send("TEST", "esdbanknotification@gmail.com", "ESDBank", recipientEmail, "<h1>This is a test<br> "+recipientFullname+" "+amount+"</h1>", "This is a test", True)

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
