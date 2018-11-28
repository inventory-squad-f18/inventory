"""
    Module for Unit Testing models.py file
"""


import unittest
import os
import json
import time
from mock import patch
from app.models import Inventory, DataValidationError
from app import app



VCAP_SERVICES = {
    'cloudantNoSQLDB': [
        {'credentials': {
            'username': 'admin',
            'password': 'pass',
            'host': '127.0.0.1',
            'port': 5984,
            'url': 'http://admin:pass@127.0.0.1:5984'
            }
        }
    ]
}

class TestModels(unittest.TestCase):
    """ Models Test """


    def setUp(self):
        """ Runs before each test """
        Inventory.init_db()
        Inventory.remove_all()

    def tearDown(self):
        # testing auto deployment
        # The free version of Cloudant will rate limit calls
        # to 20 lookups/sec, 10 writes/sec, and 5 queries/sec
        # so we need to pause for a bit to avoid this problem
        # if we are running in the Bluemix Pipeline
        if 'VCAP_SERVICES' in os.environ:
            time.sleep(0.5) # 1/2 second should be enough

    def test_create_a_inventory(self):
        """ Create a inventory and assert that it exists """
        item = Inventory(101, 1000, 100, 10, "new")
        self.assertTrue(item != None)
        self.assertEqual(item.id, 101)
        self.assertEqual(item.count, 1000)
        self.assertEqual(item.restock_level, 100)
        self.assertEqual(item.reorder_point, 10)
        self.assertEqual(item.condition, "new")
        # try:
        #     self.assertRaises(DataValidationError, Inventory(id=1, data=100))
        # except:
        #     pass
        try:
            self.assertRaises(DataValidationError, Inventory("test", 1000, 100, 10, "new"))
        except:
            pass
        # try:
        #     self.assertRaises(DataValidationError, Inventory(id=100, 1000, 10, "new"))
        # except:
        #     pass
        try:
            self.assertRaises(DataValidationError, Inventory(100, 1000, '100', 10, "new"))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(100, '1000', 100, 10, "new"))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(101, 1000, 100, "new", 100))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(101, 1000, 100, 10, "test"))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(101, 1000, 10, 1000, "new"))
        except:
            pass

    def test_update_a_inventory(self):
        """ Update a Inventory """
        # create a inventory with id 101 first
        item = Inventory(1, 1000, 100, 10, "new")
        item.save()
        self.assertEqual(item.id, 1)
        # Change it an save it
        item.count = 900
        item.restock_level = 90
        item.reorder_point = 9
        item.condition = 'new'
        self.assertEqual(item.id, 1)
        item.save()

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventories = Inventory.all()
        print(inventories)
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].count, 900)
        self.assertEqual(inventories[0].restock_level, 90)
        self.assertEqual(inventories[0].reorder_point, 9)


    def test_delete_a_inventory(self):
        """ Delete a Inventory """
        item = Inventory(0, 1000, 100, 10, "new")
        item.save()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(Inventory.all()), 0)

        item.delete()
        self.assertEqual(len(Inventory.all()), 0)

        item.id = 1
        item.delete()
        self.assertEqual(len(Inventory.all()), 0)


    def test_to_json(self):
        """ Test serialization of item to json """
        item = Inventory(101, 1000, 100, 10, "new")
        json_val = item.to_json()
        self.assertIsInstance(json_val, dict)
        self.assertIn('id', json_val.keys())
        self.assertIn('count', json_val.keys())
        self.assertIn('restock-level', json_val.keys())
        self.assertIn('reorder-point', json_val.keys())
        self.assertIn('condition', json_val.keys())
        self.assertEqual(json_val['id'], 101)
        self.assertEqual(json_val['count'], 1000)
        self.assertEqual(json_val['restock-level'], 100)
        self.assertEqual(json_val['reorder-point'], 10)
        self.assertEqual(json_val['condition'], "new")


    def test_from_json(self):
        """ Test deserialization of a item from json """

        data = {"id": 1, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "open-box"}
        inventory=Inventory(id=data["id"])
        item =inventory.from_json(data)
        inventory.save()
        self.assertEqual(item, None)
        self.assertEqual(inventory.id, 1)
        self.assertEqual(inventory.count, 1000)
        self.assertEqual(inventory.restock_level, 100)
        self.assertEqual(inventory.reorder_point, 10)
        self.assertEqual(inventory.condition, "open-box")
        try:
            self.assertRaises(DataValidationError, inventory.from_json("test"))
        except:
            pass
        data = {"id": 1, "count": 1000, "restock-point": 100, "reorder-point": 10, "condition": "open-box"}
        try:
            self.assertRaises(DataValidationError, inventory.from_json(data))
        except:
            pass


    # @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_init_db(self):
        """ Test if Database is initialized"""
        Inventory.init_db()
        self.assertIsNotNone(Inventory.client)
