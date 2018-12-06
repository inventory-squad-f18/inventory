from flask import jsonify, request, make_response
from flask_api import status
from service.models import Inventory, DataValidationError
from flask_restplus import Resource
from service import app, api, inventory_model

######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route('/api/inventory/<int:inventory_id>')
@api.param('inventory_id', 'The Inventory identifier')
class InventoryResource(Resource):
    """
    InventoryResource class

    Allows the manipulation of a single inventory item
    DELETE /api/inventory/{id} -  Deletes a inventory item pecified by id if it exists
    PUT /api/inventory/{id} - Updates an inventory item specified by id as per data passed in body
    GET /api/inventory/{id} - Returns an inventory item specified by id if it exists
    """
    #------------------------------------------------------------------
    # DELETE A INVENTORY
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
    # UPDATE AN EXISTING INVENTORY
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

        return message, return_code


    @api.doc('get_inventory')
    @api.response(404, 'Inventory not found')
    @api.marshal_with(inventory_model)
    def get(self, inventory_id):
        """ Retrieves a Inventory with a specific id """
        app.logger.info('Finding a inventory with id [{}]'.format(inventory_id))


        inventory = Inventory.find(inventory_id)

        # app.logger.info(inventory)
        if inventory:
            message = inventory.to_json()
            return_code = status.HTTP_200_OK
        else:
            message = {'error' : 'inventory with id: %s was not found' % str(inventory_id)}
            return_code = status.HTTP_404_NOT_FOUND

        app.logger.info(message)
        return message, return_code


@api.route('/api/inventory/reset')
class ResetInventory(Resource):

    @api.doc('delete_all_inventory')
    @api.response(204, 'Inventory deleted')
    def delete(self):
        """ Removes all pets from the database """
        Inventory.remove_all()
        return make_response('', status.HTTP_204_NO_CONTENT)
