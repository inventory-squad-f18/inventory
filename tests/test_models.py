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

    def test_update_a_inventory(self):
        """ Update a Inventory """
        # create a inventory with id 101 first
        item = Inventory(id = 1, data=(1000, 100, 10, "new"))
        item.save()
        self.assertEqual(item.id, 1)
        # Change it an save it
        item.data = (900, 90, 9, "new")
        self.assertEqual(item.id, 1)
        item.save()

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventorys = Inventory.all()
        print(inventorys)
        self.assertEqual(len(inventorys), 1)
        self.assertEqual(inventorys[0].data[0], 900)
        self.assertEqual(inventorys[0].data[1], 90)
        self.assertEqual(inventorys[0].data[2], 9)


    def test_delete_a_inventory(self):
        """ Delete a Inventory """
        item = Inventory(id = 0, data=(1000, 100, 10, "new"))
        item.save()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the pet and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(Inventory.all()), 0)


    def test_to_json(self):
        """ Test serialization of item to json """
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


    def test_from_json(self):
        """ Test deserialization of a item from json """

        data = {"id": 1, "count": 1000, "restock-level": 100, "reorder-point": 10, "condition": "open-box"}
        inventory=Inventory(id=data["id"],data=(0,2,1,"new"))
        # test if not dict
        item =inventory.from_json(data)
        inventory.save()
        self.assertEqual(item, None)
        self.assertEqual(inventory.id, 1)
        self.assertEqual(inventory.data[0], 1000)
        self.assertEqual(inventory.data[1], 100)
        self.assertEqual(inventory.data[2], 10)
        self.assertEqual(inventory.data[3], "open-box")
        try:
            self.assertRaises(DataValidationError, inventory.from_json("test"))
        except:
            pass
        data = {"id": 1, "count": 1000, "restock-point": 100, "reorder-point": 10, "condition": "open-box"}
        try:
            self.assertRaises(DataValidationError, inventory.from_json(data))
        except:
            pass
