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
