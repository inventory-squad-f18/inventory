"""
    This module holds the model for our application
"""

import os
import json
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import ConnectionError

class DataValidationError(Exception):
    """ Used for an data validation errors when getting object from JSON """
    pass

class Inventory(object):
    data = []
    database = None
    client = None
    logger = logging.getLogger(__name__)



    def __init__(self, id, count = None, restock_level = None, reorder_point = None, condition = None):
        if not isinstance(id, int):
            raise DataValidationError("Invalid data: expected int in id, received " + type(id))
        try:
            Inventory.validate_data(count, restock_level, reorder_point, condition)
        except:
            raise
        self.id = id
        if count is not None:
            self.count = count
        if restock_level is not None:
            self.restock_level = restock_level
        if reorder_point is not None:
            self.reorder_point = reorder_point
        if condition is not None:
            self.condition = condition


    @classmethod
    def validate_data(cls, count, restock_level, reorder_point, condition):
        # if not isinstance(data, tuple):
            # raise DataValidationError("Invalid data: expected tuple in data, received " + type(data))
        # if len(data) != 4:
        #     raise DataValidationError("Expected 4 fields: count:int, restock-level:int, reorder-point:int, condition:string(new, open-box, used)")
        if count is not None and not isinstance(count, int):
            raise DataValidationError("Invalid data: expected int in count, received " + type(data[0]))
        if restock_level is not None and not isinstance(restock_level, int):
            raise DataValidationError("Invalid data: expected int in restock_level, received " + type(data[1]))
        if reorder_point is not None and not isinstance(reorder_point, int):
            raise DataValidationError("Invalid data: expected int in reorder_point, received " + type(data[0]))
        if restock_level is not None and reorder_point is not None and reorder_point >= restock_level:
            raise DataValidationError("Invalid data: expected ordering: restock_level < reorder_point")
        if condition is not None and condition not in ["new", "open-box", "used"]:
            raise DataValidationError("Invalid data: expected value of condition is 'new' or 'open-box' or 'used'")


    def save(self):
        """
        Saves a Inventory to the data store
        """
        # if id is duplicate?, if needs update
        #Inventory.data.append(self)

        id_list = [item.id for item in Inventory.data]
        if self.id not in id_list:
            Inventory.data.append(self)
        else:
            for i in range(len(Inventory.data)):
                if Inventory.data[i].id == self.id:
                    Inventory.data[i] = self
                    break

    def delete(self):
        """ Removes a Invengory from the data store """
        Inventory.data.remove(self)


    def to_json(self):
        """ serializes an inventory item into an dictionary """
        return {"id": self.id, "count": self.count, "restock-level": self.restock_level, "reorder-point": self.reorder_point, "condition": self.condition}


    def from_json(self,json_val):
        """ deserializes inventory item from an dictionary """
        if not isinstance(json_val, dict):
            raise DataValidationError("Invalid data: expected dict, received " + type(json_val))
        try:
            Inventory.validate_data(json_val['count'], json_val['restock-level'], json_val['reorder-point'], json_val['condition'])
            self.count = json_val['count']
            self.restock_level = json_val['restock-level']
            self.reorder_point = json_val['reorder-point']
            self.condition = json_val['condition']
        except DataValidationError:
            raise
        except KeyError as error:
            raise DataValidationError("Invalid data: missing " + error.args[0])
        return

    @classmethod
    def find(cls, inventory_id):
        """ Finds a inventory by it's ID """
        print "cls.data ",cls,cls.data
        if not cls.data:
            return None
        inventory = [inventory for inventory in cls.data if inventory.id == inventory_id]
        if inventory:
            return inventory[0]
        return None

    @classmethod
    def find_by_condition(cls, condition):
        """ Finds a inventory by it's ID """
        print "cls.data ",cls,cls.data
        if condition not in ["new", "open-box", "used"]:
            raise DataValidationError("Invalid data: expected value of condition is 'new' or 'open-box' or 'used'")
        if not cls.data:
            return None
        inventory = [inventory for inventory in cls.data if inventory.condition == condition]
        return inventory

    @classmethod
    def find_reorder_items(cls):
        if not cls.data:
            return None

        inventory = [inventory for inventory in cls.data if inventory.count <= inventory.reorder_point]
        return inventory

    @classmethod
    def all(cls):
        """ Returns all of the Inventorys in the database """
        return [inventory for inventory in cls.data]

    @staticmethod
    def init_db(dbname='inventory'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        vcap_services = {}
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Inventory.logger.info('Running in Bluemix mode.')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        else:
            Inventory.logger.info('VCAP_SERVICES undefined.')
            creds = {
                "username": "admin",
                "password": "pass",
                "host": '127.0.0.1',
                "port": 5984,
                "url": "http://admin:pass@127.0.0.1:5984/"
            }
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

        # Look for Cloudant in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('cloudantNoSQLDB'):
                cloudant_service = vcap_services[service][0]
                opts['username'] = cloudant_service['credentials']['username']
                opts['password'] = cloudant_service['credentials']['password']
                opts['host'] = cloudant_service['credentials']['host']
                opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = cloudant_service['credentials']['url']

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            Inventory.logger.info('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')
            exit(-1)

        Inventory.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            Inventory.client = Cloudant(opts['username'],
                                  opts['password'],
                                  url=opts['url'],
                                  connect=True,
                                  auto_renew=True
                                 )
        except ConnectionError:
            raise AssertionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Inventory.database = Inventory.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Inventory.database = Inventory.client.create_database(dbname)
        # check for success
        if not Inventory.database.exists():
            raise AssertionError('Database [{}] could not be obtained'.format(dbname))
