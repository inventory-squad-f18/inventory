from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status
from service.models import Inventory, DataValidationError
from flask_restplus import Api, Resource, fields, reqparse
from service import app, api, inventory_model

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
