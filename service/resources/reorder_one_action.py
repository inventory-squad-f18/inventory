from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status
from service.models import Inventory, DataValidationError
from flask_restplus import Api, Resource, fields, reqparse
from service import app, api, inventory_model

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
