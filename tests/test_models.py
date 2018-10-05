"""
    Module for Unit Testing models.py file
"""


import unittest
from app.models import Inventory, DataValidationError
from app import app

class TestModels(unittest.TestCase):
    """ Models Test """
    def test_create_a_inventory(self):
        """ Create a inventory and assert that it exists """
        item = Inventory(id= 101, data=(1000, 100, 10, "new"))
        self.assertTrue(item != None)
        self.assertEqual(item.id, 101)
        self.assertEqual(item.data[0], 1000)
        self.assertEqual(item.data[1], 100)
        self.assertEqual(item.data[2], 10)
        self.assertEqual(item.data[3], "new")
        try:
            self.assertRaises(DataValidationError, Inventory(id=1, data=100))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id="test", data=(1000, 100, 10, "new")))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=100, data=(1000, 10, "new")))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=100, data=(1000, '100', 10, "new")))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=100, data=('1000', 100, 10, "new")))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=101, data=(1000, 100, "new", 100)))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=101, data=(1000, 100, 10, "test")))
        except:
            pass
        try:
            self.assertRaises(DataValidationError, Inventory(id=101, data=(1000, 10, 1000, "new")))
        except:
            pass

    def test_to_json(self):
        item = Inventory(id= 101, data=(1000, 100, 10, "new"))
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
