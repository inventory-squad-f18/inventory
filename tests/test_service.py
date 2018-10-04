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

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(unittest.TestCase):
    """ Inventory Service Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = service.app.test_client()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Inventory REST API Service')

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
        self.assertTrue(len(self.app.logger.handlers) > 0)
