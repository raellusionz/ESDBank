#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/activity_log", methods=['POST'])
def receiveActivityLog():
    # Check if the request contains valid JSON
    activity_log = None
    if request.is_json:
        activity_log = request.get_json()
        processActivityLog(activity_log)
        # reply to the HTTP request
        return jsonify({"code": 200, "data": 'OK. Activity log printed.'}), 200 # return message; can be customized
    else:
        activity_log = request.get_data()
        print("Received an invalid log:")
        print(activity_log)
        print()
        return jsonify({"code": 400, "message": "Activity log input should be in JSON."}), 400 # Bad Request

def processActivityLog(details):
    print("Recording a log:")
    print(details)
    print() # print a new line feed as a separator


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("This is flask for " + os.path.basename(__file__) + ": recording activity logs ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
