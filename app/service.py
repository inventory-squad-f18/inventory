"""
    This module holds the controller for our application
"""

import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status
from models import Inventory, DataValidationError
from flask_restplus import Api, Resource, fields, reqparse

#import flask application
from . import app
# from models import Inventory



# Test CI/CD
# # Status Codes
# HTTP_200_OK = 200
# HTTP_201_CREATED = 201
# HTTP_204_NO_CONTENT = 204
# HTTP_400_BAD_REQUEST = 400
# HTTP_404_NOT_FOUND = 404
# HTTP_409_CONFLICT = 409

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is Inventory store server.',
          doc='/'
          # prefix='/api'
         )

# This namespace is the start of the path i.e., /inventory
ns = api.namespace('inventory', description='Inventory')

# Define the model so that the docs reflect what can be sent
inventory_model = api.model('Inventory', {
    'id': fields.Integer(required=True,
                         description='The unique id assigned to item'),
    'count': fields.Integer(required=True,
                          description='The count of item'),
    'restock-level': fields.Integer(required=True,
                              description='The restock level'),
    'reorder-point': fields.Integer(required=True,
                                description='Reorder point'),
    'condition': fields.String(required=True,
                              description='The condition of item')
})

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Inventory REST API Service',
                   version='1.0',
                   url=url_for('list_inventory', _external=True)), status.HTTP_200_OK

inventory_args = reqparse.RequestParser()
inventory_args.add_argument('condition', type=str, required=False, help='List inventory by condition')

######################################################################
# LIST ALL INVENTORY
######################################################################
# @app.route('/inventory', methods=['GET'])
# def list_inventory():
#     """ Retrieves a list of inventory from the database """
#     results = []
#     condition = request.args.get('condition')
#     if condition:
#         try:
#             results = Inventory.find_by_condition(condition)
#         except DataValidationError as error:
#             return jsonify({'error' : str(error)}), status.HTTP_400_BAD_REQUEST
#     else:
#         results = Inventory.all()

#     return jsonify([inventory.to_json() for inventory in results]), status.HTTP_200_OK


@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interactions with collections of Pets """

    @api.doc('list_inventory')
    #@api.param('category', 'List Pets by category')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """ Returns all of the Pets """
        app.logger.info('Request to list inventory...')
        inventories = []
        args = inventory_args.parse_args()
        condition = args['condition']
        if condition:
            try:
              inventories = Inventory.find_by_condition(condition)
            except DataValidationError as error:
                return jsonify({'error' : str(error)}), status.HTTP_400_BAD_REQUEST
        else:
            inventories = Inventory.all()

        app.logger.info('[%s] Inventories returned', len(inventories))
        results = [inventory.to_json() for inventory in inventories]

        # return jsonify([inventory.to_json() for inventory in inventories]), status.HTTP_200_OK
        return results, status.HTTP_200_OK


######################################################################
# RETRIEVE A Inventory
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """ Retrieves a Inventory with a specific id """
    app.logger.info('Finding a inventory with id [{}]'.format(inventory_id))


    inventory = Inventory.find(inventory_id)
    if inventory:
        message = inventory.to_json()
        return_code = status.HTTP_200_OK
    else:
        message = {'error' : 'inventory with id: %s was not found' % str(inventory_id)}
        return_code = status.HTTP_404_NOT_FOUND

    return jsonify(message), return_code


######################################################################
# ADD A NEW Inventory
######################################################################
@app.route('/inventory', methods=['POST'])
def create_inventory():
    """ Creates a inventory, not persistent """
    app.logger.info('Creating a new inventory')

    payload = request.get_json()

    inventory = Inventory.find(payload['id'])
    if inventory is not None:
        return jsonify({'error' : 'Inventory with id: %s already exists' % str(payload['id'])}), status.HTTP_400_BAD_REQUEST

    inventory=Inventory(id=payload["id"])
    try:
        inventory.from_json(payload)
    except DataValidationError as error:
        return jsonify({'error' : str(error)}), status.HTTP_400_BAD_REQUEST
    inventory.save()
    message = inventory.to_json()
    response = make_response(jsonify(message), status.HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_inventory', inventory_id=inventory.id, _external=True)
    return response

######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    """ Updates a Inventory in the database """
    app.logger.info('Updating a inventory')
    inventory = Inventory.find(inventory_id)
    if inventory:
        print "find inventory ",inventory.to_json()
        payload = request.get_json()
        payload["id"]=inventory_id
        app.logger.info("payload " + str(payload) + str(type(payload)) + str(inventory.to_json()))
        try:
            inventory.from_json(payload)
        except DataValidationError as error:
            return jsonify({'error': str(error)}), status.HTTP_400_BAD_REQUEST

        inventory.save()
        message = inventory.to_json()
        return_code = status.HTTP_200_OK
    else:
        message = {'error' : 'Inventory with id: %s was not found' % str(id)}
        return_code = status.HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# DELETE A Inventory
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    """ Removes a Inventory from the database that matches the id """
    app.logger.info('Deleting a inventory')
    inventory = Inventory.find(inventory_id)
    if inventory:
        inventory.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


@app.route('/inventory/reorder', methods=['PUT'])
def reorder():
    app.logger.info('Reordering Items')

    Inventory.reorder_items()
    return jsonify({}),status.HTTP_200_OK


@app.route('/inventory/<int:inventory_id>/reorder', methods=['PUT'])
def reorder_item(inventory_id):
    app.logger.info('Reordering Item :: ' + str(inventory_id))

    Inventory.reorder_items(inventory_id)
    return jsonify({}),status.HTTP_200_OK


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
