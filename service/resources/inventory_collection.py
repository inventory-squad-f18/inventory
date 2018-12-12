from flask import request, jsonify
from flask_api import status
from service.models import Inventory, DataValidationError
from flask_restplus import Resource, fields, reqparse
from service import app, api, inventory_args, inventory_model
from . import InventoryResource

######################################################################
#  PATH: /api/inventory
######################################################################
@api.route('/api/inventory', strict_slashes=False)
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
                return {'message' : str(error)}, status.HTTP_400_BAD_REQUEST
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
        return inventory.to_json(), status.HTTP_201_CREATED, {'Location': api.url_for(InventoryResource, inventory_id=inventory.id, _external=True)}
