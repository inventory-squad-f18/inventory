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
from . import app

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is Inventory store server.',
          doc='/'
         )

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

inventory_args = reqparse.RequestParser()
inventory_args.add_argument('condition', type=str, required=False, help='List inventory by condition')

######################################################################
#  PATH: /inventory
######################################################################
@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """
    InventoryCollection class

    Allows the manipulation of inventory item/s
    GET /inventory - Returns all inventory items present in system
    POST /inventory -  Inserts new inventory item in system as specified by data passed in body
    """

    #------------------------------------------------------------------
    # LIST ALL INVENTORIES
    #------------------------------------------------------------------
    @api.doc('list_inventory')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """ Return all the items present in inventory """
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
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW INVENTORY
    #------------------------------------------------------------------
    @api.doc('create_inventory')
    @api.expect(inventory_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Inventory created successfully')
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates a Inventory based on the data passed in the body
        """
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
        return inventory.to_json(), status.HTTP_201_CREATED, {'Location': url_for('get_inventory', inventory_id=inventory.id, _external=True)}


######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route('/inventory/<int:inventory_id>')
@api.param('inventory_id', 'The Inventory identifier')
class InventoryResource(Resource):
    """
    InventoryResource class

    Allows the manipulation of a single inventory item
    DELETE /inventory/{id} -  Deletes a inventory item pecified by id if it exists
    PUT /inventory/{id} - Updates an inventory item specified by id as per data passed in body
    GET /inventory/{id} - Returns an inventory item specified by id if it exists
    """
    #------------------------------------------------------------------
    # DELETE A PET
    #------------------------------------------------------------------
    @api.doc('delete_inventory')
    @api.response(204, 'Inventory deleted')
    def delete(self, inventory_id):
        """
        Delete a inventory item specified by id if it exists
        """
        app.logger.info('Request to Delete a inventory with id [%s]', inventory_id)
        inventory = Inventory.find(inventory_id)
        if inventory:
            inventory.delete()
        return '', status.HTTP_204_NO_CONTENT


    #------------------------------------------------------------------
    # UPDATE AN EXISTING PET
    #------------------------------------------------------------------
    @api.doc('update_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.response(200, 'Inventory Updated')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, inventory_id):
        """
        Update a Inventory specified by id as per data passed in body
        """
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


    @api.doc('get_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(200, 'Inventory returned')
    @api.marshal_with(inventory_model)
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
#  PATH: /inventory/reorder
######################################################################
@api.route('/inventory/reorder')
class ReorderAllAction(Resource):
    """
    ReorderAllAction class

    Allows reordering multiple inventory items
    PUT /inventory/reorder - Reorders all inventory items whose count is less than restock level
    """
    @api.doc('reorder_items')
    @api.marshal_with(inventory_model)
    def put(self):
        "Reorder all the items whose count is less than restock level"
        app.logger.info('Reordering Items')

        Inventory.reorder_items()
        return jsonify({}),status.HTTP_200_OK


######################################################################
#  PATH: /inventory/{id}/reorder
######################################################################
@api.route('/inventory/<int:inventory_id>/reorder')
@api.param('inventory_id', 'The Inventory identifier')
class ReorderOneAction(Resource):
    """
    ReorderOneAction class

    Allows reordering single inventory item
    PUT /inventory/{id}/reorder - Reorders inventory item specified by id if its count is less than restock level
    """
    @api.doc('reorder_items')
    @api.marshal_with(inventory_model)
    def put(self, inventory_id):
        "Reorders item specified by id if it's count is less than restock level"
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
