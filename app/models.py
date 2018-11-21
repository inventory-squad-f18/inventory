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
            raise DataValidationError("Invalid data: expected int in id, received " + str(type(id)))
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
        try:
            document = self.database[str(self.id)]
        except KeyError:
            document = None
        doc = self.to_json()
        doc['_id'] = str(doc['id'])
        del doc['id']
        if document:
            document.update(doc)
            document.save()
        else:
            document = self.database.create_document(doc)


    def delete(self):
        """ Removes a Invengory from the data store """
        try:
            document = self.database[str(self.id)]
        except KeyError:
            document = None
        if document:
            document.delete()


    def to_json(self):
        """ serializes an inventory item into an dictionary """
        return {"id": self.id, "count": self.count, "restock-level": self.restock_level, "reorder-point": self.reorder_point, "condition": self.condition}


    def from_json(self,json_val):
        """ deserializes inventory item from an dictionary """
        if not isinstance(json_val, dict):
            raise DataValidationError("Invalid data: expected dict, received " + type(json_val))
        try:
            Inventory.validate_data(json_val['count'], json_val['restock-level'], json_val['reorder-point'], json_val['condition'])
            # self.id = json_val['id']
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
        if not cls.database:
            return None
        try:
            document = cls.database[str(inventory_id)]
            inventory = Inventory(int(document['_id']))
            inventory.from_json(document)
            return inventory
        except KeyError as err:
            return None

    @classmethod
    def find_by_condition(cls, condition):
        """ Finds a inventory by it's ID """
        if condition not in ["new", "open-box", "used"]:
            raise DataValidationError("Invalid data: expected value of condition is 'new' or 'open-box' or 'used'")
        if not cls.database:
            return None

        results = []

        for doc in cls.database:
            if doc['condition'] == condition:
                inventory = Inventory(int(doc['_id']))
                inventory.from_json(doc)
                results.append(inventory)

        return results

    @classmethod
    def find_reorder_items(cls):
        if not cls.database:
            return None

        results = []
        for doc in cls.database:
            if doc['count'] <= doc['reorder-point']:
                inventory = Inventory(int(doc['_id']))
                inventory.from_json(doc)
                results.append(inventory)

        return results

    @classmethod
    def all(cls):
        """ Returns all of the Inventorys in the database """
        results = []

        for doc in cls.database:
            inventory = Inventory(int(doc['_id']))
            inventory.from_json(doc)
            results.append(inventory)
        return results

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

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
