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
import app.service as service
from app.models import Inventory
from time import sleep

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(unittest.TestCase):
    """ Inventory Service Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = service.app.test_client()
        sleep(0.5)
        Inventory.init_db()
        sleep(0.5)
        Inventory.remove_all()
        sleep(0.5)

    def tearDown(self):
        """ Runs after each test """
        sleep(0.5)
        Inventory.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Inventory REST API Service')

    def test_get_inventory(self):
        """ Get one inventory """
        item = Inventory(101, 1000, 100, 10, "used")
        item.save()
        resp = self.app.get('/inventory/101')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['condition'], "used")

    def test_get_inventory_not_found(self):
        """ Get one inventory that does not exist """
        # when no inventory in
        resp = self.app.get('/inventory/100')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # when the specific inventory in
        item = Inventory(101, 1000, 100, 10, "used")
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

        resp = self.app.post('/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        new_inventory = {"id": 100, "count": 1000, "restock-level": 100, "reorder-point": 101, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.post('/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory(self):
        """ Update an existing Inventory """
        # create a inventory with id 101 first
        # item = Inventory(id = 101, data=(1000, 100, 10, "new"))
        # item.save()
        inventory1 = {"id": 101, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/inventory', data=data, content_type='application/json')
        # update the inventory with id 101
        new_inventory = {"count": 900, "restock-level": 90, "reorder-point": 9, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/inventory/101', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/inventory/101', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)

        self.assertEqual(new_json['count'], 900)
        self.assertEqual(new_json['restock-level'], 90)
        self.assertEqual(new_json['reorder-point'], 9)

        new_inventory = {"count": 900, "restock-level": 100, "reorder-point": 101, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/inventory/101', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_not_found(self):
        """ Update a Inventory that can't be found """
        new_inventory = {"count": 900, "restock-level": 90, "reorder-point": 9, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/inventory/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_inventory(self):
        """ Delete a Inventory that exists """
        # save the current number of inventory for later comparrison
        inventory = {"id": 1, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        inventory_count = self.get_inventory_count()

        # delete a inventory
        resp = self.app.delete('/inventory/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_inventory_count()
        self.assertEqual(new_count, inventory_count - 1)

        resp = self.app.delete('/inventory/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


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


    def test_list_inventory(self):
        """ Test list inventory """
        self.assertEqual(self.get_inventory_count(), 0)

        # create inventories
        inventory1 = {"id": 101, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        # LIST INVENTORIES
        self.assertEqual(self.get_inventory_count(), 2)
        self.assertEqual(self.get_inventory_count(condition = 'new'), 1)


        resp = self.app.get('/inventory', query_string = {'condition': "NEW"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_reorder(self):
        """ Test reorder action """
        inventory1 = {"id": 101, "count": 9, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 49, "restock-level": 100, "reorder-point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        resp = self.app.put('/inventory/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/inventory')
        data = json.loads(resp.data)

        for item in data:
            self.assertEqual(item['count'], item['restock-level'])

        Inventory.remove_all()

        inventory1 = {"id": 101, "count": 101, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        resp = self.app.put('/inventory/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/inventory')
        data = json.loads(resp.data)

        for item in data:
            self.assertTrue(item['count'] != item['restock-level'])

        Inventory.remove_all()

        inventory1 = {"id": 101, "count": 60, "restock-level": 100, "reorder-point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 49, "restock-level": 100, "reorder-point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/inventory', data=data, content_type='application/json')

        resp = self.app.put('/inventory/101/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/inventory')
        data = json.loads(resp.data)

        for item in data:
            if item['id'] == 101:
                self.assertTrue(item['count'] == item['restock-level'])

######################################################################
# Utility functions
######################################################################

    def get_inventory_count(self, condition = None):
        # save the current number of inventory
        print condition
        if condition:
            resp = self.app.get('/inventory', query_string = {'condition': condition})
        else:
            resp = self.app.get('/inventory')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)
