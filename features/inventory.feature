Feature: The inventory service back-end
    As a E-Commerce Website
    I need a RESTful inventory service
    So that I can keep track of all my inventories

Background:
    Given the following inventories
        | id   | count    | restock_level | condition | reorder_point |
        | 101  | 1000     | 100           | new       | 10            |
        | 102  | 500      | 30            | open-box  | 5             |
        | 103  | 5        | 100           | open-box  | 10            |

    Scenario: Get one Inventory
        When I visit the "Home Page"
        And I set the "Id" to "102"
        And I press the "Retrieve" button
        Then I should see "open-box" in the "Condition" field

    Scenario: Get Inventory that does not exist
        When I visit the "Home Page"
        And I set the "Id" to "104"
        And I press the "Update" button
        Then I should see the "Inventory with id: 104 was not found"

    Scenario: Create a Inventory
        When I visit the "Home Page"
        And I set the "Id" to "104"
        And I set the "Count" to "1000"
        And I set the "restock_level" to "300"
        And I set the "reorder_point" to "100"
        And I set the "Condition" to "new"
        And I press the "Create" button
        Then I should see the "Success"

    Scenario: List all inventories
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see "101" in the results
        And I should see "102" in the results
        And I should see "open-box" in the results

    Scenario: List all inventories with invalid condition
        When I visit the "Home Page"
        And I set the "Id" to "102"
        And I set the "Condition" to "abc"
        And I press the "Search" button
        Then I should see the "Invalid data: expected value of condition is 'new' or 'open-box' or 'used'"

    Scenario: Delete one Inventory
        When I visit the "Home Page"
        And I set the "Id" to "101"
        And I press the "Delete" button
        And I press the "Search" button
        Then I should not see "new" in the results

    Scenario: Update one Inventory
        When I visit the "Home Page"
        And I set the "Id" to "101"
        And I press the "Retrieve" button
        Then I should see "new" in the "Condition" field
        When I change "Count" to "1001"
        And I press the "Update" button
        Then I should see the "Success"
        When I set the "Id" to "101"
        And I press the "Retrieve" button
        Then I should see "1001" in the "Count" field

    Scenario: Update with Invalid data
        When I visit the "Home Page"
        And I set the "Id" to "102"
        And I set the "Condition" to "abc"
        And I press the "Update" button
        Then I should see the "Invalid data: expected value of condition is 'new' or 'open-box' or 'used'"

    Scenario: Update Inventory that does not exist
        When I visit the "Home Page"
        And I set the "Id" to "104"
        And I press the "Update" button
        Then I should see the "Inventory with id: 104 was not found"

    Scenario: Reorder one Inventory
        When I visit the "Home Page"
        And I set the "Id" to "103"
        And I press the "Retrieve" button
        Then I should see "5" in the "Count" field
        When I press the "Reorder" button
        Then I should see the "Success"
        When I set the "Id" to "103"
        And I press the "Retrieve" button
        Then I should see "100" in the "Count" field

    Scenario: Query inventory
        When I visit the "Home Page"
        And I set the "Condition" to "new"
        And I press the "Search" button
        Then I should see "new" in the results
        And I should not see "open-box" in the results
