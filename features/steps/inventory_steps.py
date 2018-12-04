"""
Inventory Steps
Steps file for Inventory.feature
"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions

# WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')


#@given(u'the server is started')
#def step_impl(context):
#    context.app = server.app.test_client()
#    context.server = server

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    context.resp = requests.get(context.base_url)
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)
