"""
    This module holds the controller for our application
"""

import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status
# from models import Inventory, DataValidationError

#import flask application
from . import app
from models import Inventory



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
                   url=url_for('list_inventory', _external=True)), status.HTTP_200_OK


######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route('/inventory', methods=['GET'])
def list_inventory():
    return


######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """ Retrieves a Pet with a specific id """
    app.logger.info('Finding a inventory with id [{}]'.format(inventory_id))

    inventory = Inventory.find(inventory_id)
    if inventory:
        message = inventory.to_json()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'inventory with id: %s was not found' % str(inventory_id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/inventory', methods=['POST'])
def create_inventory():
    """ Creates a inventory, not persistent """
    app.logger.info('Creating a new inventory')
    payload = request.get_json()
    inventory = Inventory.from_json(payload)
    message = inventory.to_json()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_inventory', inventory_id=inventory.id, _external=True)
    return response

######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
