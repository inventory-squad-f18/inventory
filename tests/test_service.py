"""
Test cases for the Inventory Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
from flask import Flask
#from app.models import DataValidationError
import app.service as service
from app.models import Inventory

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(unittest.TestCase):
    """ Inventory Service Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = service.app.test_client()
    def tearDown(self):
        """ Runs after each test """
        Inventory.data=[]

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Inventory REST API Service')

    def test_get_inventory(self):
        """ Get one inventory """
        item = Inventory(id= 101, data=(1000, 100, 10, "used"))
        item.save()
        resp = self.app.get('/inventory/101')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['condition'], "used")

    def test_get_inventory_not_found(self):
        """ Get one inventory """
        # when no inventory in
        resp = self.app.get('/inventory/100')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # when the specific inventory in
        item = Inventory(id= 101, data=(1000, 100, 10, "used"))
        item.save()
        resp = self.app.get('/inventory/100')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_inventory(self):
        """ Create a Inventory """
        # add a new pet
        # new_inventory = {"id": 101, "data":(1000, 100, 10, "new") }
        new_inventory = {"id": 101, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "new"}

        data = json.dumps(new_inventory)
        resp = self.app.post('/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['id'], 101)
        self.assertEqual(new_json['count'], 1000)
        self.assertEqual(new_json, new_inventory)

    def test_initialize_logging(self):
        """ Test the Logging Service """

        #test client does not have logger
        #hence initialized it with flask application
        self.app = Flask(__name__)
        self.app.debug = False

        #remove all the logger handlers so that the list of handlers is empty
        handler_list = list(self.app.logger.handlers)
        for log_handler in handler_list:
            self.app.logger.removeHandler(log_handler)

        #initialize and check whether there is atleast one logger handler
        service.initialize_logging()
        self.assertTrue(len(self.app.logger.handlers) == 1)

        #test whether our function is removing previous handlers correctly
        service.initialize_logging()
        self.assertTrue(len(self.app.logger.handlers) == 1)
