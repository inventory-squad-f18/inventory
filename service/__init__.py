"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import os
import sys
import logging
from flask import Flask
from flask_restplus import Api, fields, reqparse
from .models import Inventory, DataValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

Inventory.logger = app.logger;

@app.route('/')
def index():
    return app.send_static_file('index.html')


api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is Inventory store server.',
          doc='/api/'
         )

# Define the model so that the docs reflect what can be sent
inventory_model = api.model('Inventory', {
    'id': fields.Integer(required=True,
                         description='The unique id assigned to item'),
    'count': fields.Integer(required=True,
                          description='The count of item'),
    'restock_level': fields.Integer(required=True,
                              description='The restock level'),
    'reorder_point': fields.Integer(required=True,
                                description='Reorder point'),
    'condition': fields.String(required=True,
                              description='The condition of item'),
    'message': fields.String(required=True, description='error message') #message defined so that we can return error message
})

inventory_args = reqparse.RequestParser()
inventory_args.add_argument('condition', type=str, required=False, help='List inventory by condition')

from service.resources import InventoryResource
from service.resources import InventoryCollection
from service.resources import ReorderAllAction
from service.resources import ReorderOneAction
from service.resources import ResetInventory

# Set up logging for production
print 'Setting up logging for {}...'.format(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

app.logger.info('************************************************************')
app.logger.info('        I N V E N T O R Y   R E S T   A P I   S E R V I C E ')
app.logger.info('************************************************************')
app.logger.info('Logging established')


@app.before_first_request
def init_db():
    """ Initlaize the model """
    Inventory.init_db()
