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
from service import app
from service.models import Inventory
from time import sleep


######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(unittest.TestCase):
    """ Inventory Service Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = app.test_client()
        sleep(0.5)
        Inventory.init_db()
        sleep(0.5)
        Inventory.remove_all()
        sleep(0.5)

    def tearDown(self):
        """ Runs after each test """
        sleep(0.5)
        Inventory.remove_all()

    def test_get_inventory(self):
        """ Get one inventory """
        item = Inventory(101, 1000, 100, 10, "used")
        item.save()
        resp = self.app.get('/api/inventory/101')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        print data
        self.assertEqual(data['condition'], "used")

    def test_get_inventory_not_found(self):
        """ Get one inventory that does not exist """
        # when no inventory in
        resp = self.app.get('/api/inventory/100')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # when the specific inventory in
        item = Inventory(101, 1000, 100, 10, "used")
        item.save()
        resp = self.app.get('/api/inventory/100')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_inventory(self):
        """ Create a Inventory """
        new_inventory = {"id": 101, "count": 1000, "restock_level": 100, "reorder_point": 10, "condition": "new"}

        data = json.dumps(new_inventory)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_inventory['message'] = None
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['id'], 101)
        self.assertEqual(new_json['count'], 1000)
        self.assertEqual(new_json, new_inventory)

        resp = self.app.post('/api/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        new_inventory = {"id": 100, "count": 1000, "restock_level": 100, "reorder_point": 101, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory(self):
        """ Update an existing Inventory """
        # create a inventory with id 101 first
        inventory1 = {"id": 101, "count": 1000, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        # update the inventory with id 101
        new_inventory = {"count": 900, "restock_level": 90, "reorder_point": 9, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/api/inventory/101', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/api/inventory/101', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)

        self.assertEqual(new_json['count'], 900)
        self.assertEqual(new_json['restock_level'], 90)
        self.assertEqual(new_json['reorder_point'], 9)

        new_inventory = {"count": 900, "restock_level": 100, "reorder_point": 101, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/api/inventory/101', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_inventory_not_found(self):
        """ Update a Inventory that can't be found """
        new_inventory = {"count": 900, "restock_level": 90, "reorder_point": 9, "condition": "new"}
        data = json.dumps(new_inventory)
        resp = self.app.put('/api/inventory/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_inventory(self):
        """ Delete a Inventory that exists """
        # save the current number of inventory for later comparrison
        inventory = {"id": 1, "count": 1000, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        inventory_count = self.get_inventory_count()

        # delete a inventory
        resp = self.app.delete('/api/inventory/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_inventory_count()
        self.assertEqual(new_count, inventory_count - 1)

        resp = self.app.delete('/api/inventory/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_inventory(self):
        """ Test list inventory """
        self.assertEqual(self.get_inventory_count(), 0)
        self.assertEqual(self.get_inventory_count(condition = 'new'), 0)

        # create inventories
        inventory1 = {"id": 101, "count": 1000, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 1000, "restock_level": 100, "reorder_point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        # LIST INVENTORIES
        self.assertEqual(self.get_inventory_count(), 2)
        self.assertEqual(self.get_inventory_count(condition = 'new'), 1)


        resp = self.app.get('/api/inventory', query_string = {'condition': "NEW"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_reorder(self):
        """ Test reorder action """
        resp = self.app.put('/api/inventory/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        inventory1 = {"id": 101, "count": 9, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 49, "restock_level": 100, "reorder_point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        sleep(0.5)
        resp = self.app.put('/api/inventory/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/api/inventory')
        data = json.loads(resp.data)

        for item in data:
            self.assertEqual(item['count'], item['restock_level'])

        sleep(0.5)
        Inventory.remove_all()

        inventory1 = {"id": 101, "count": 101, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        resp = self.app.put('/api/inventory/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        sleep(0.5)
        resp = self.app.get('/api/inventory')
        data = json.loads(resp.data)

        for item in data:
            self.assertTrue(item['count'] != item['restock_level'])

        sleep(0.5)
        Inventory.remove_all()

        inventory1 = {"id": 101, "count": 60, "restock_level": 100, "reorder_point": 10, "condition": "new"}
        data = json.dumps(inventory1)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        inventory2 = {"id": 102, "count": 49, "restock_level": 100, "reorder_point": 10, "condition": "open-box"}
        data = json.dumps(inventory2)
        resp = self.app.post('/api/inventory', data=data, content_type='application/json')

        sleep(0.5)
        resp = self.app.put('/api/inventory/101/reorder')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/api/inventory')
        data = json.loads(resp.data)

        for item in data:
            if item['id'] == 101:
                self.assertTrue(item['count'] == item['restock_level'])

######################################################################
# Utility functions
######################################################################

    def get_inventory_count(self, condition = None):
        # save the current number of inventory
        print condition
        if condition:
            resp = self.app.get('/api/inventory', query_string = {'condition': condition})
        else:
            resp = self.app.get('/api/inventory')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)
