"""
    This module holds the controller for our application
"""

import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
# from models import Pet, DataValidationError

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Inventory REST API Service',
                   version='1.0',
                   url=url_for('list_inventory', _external=True)), HTTP_200_OK


######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route('/inventory', methods=['GET'])
def list_inventory():
    return

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "*********************************"
    print " I N V E N T O R Y   S E R V I C E "
    print "*********************************"
    # dummy data for testing
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
