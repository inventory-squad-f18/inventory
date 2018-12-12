"""
Inventory Steps
Steps file for Inventory.feature
"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')


@given('the following inventories')
def step_impl(context):
    """ Delete all inventory items and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/api/inventory/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/api/inventory'
    for row in context.table:
        data = {
            "id": int(row["id"]),
            "condition": row['condition'],
            "count": int(row["count"]),
            "restock_level": int(row["restock_level"]),
            "reorder_point": int(row["reorder_point"])
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    context.resp = requests.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'title'),
            message
        )
    )
    expect(found).to_be(True)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'inventory_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = 'inventory_' + element_name.lower()
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@then('I should see the "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)
