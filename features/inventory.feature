Feature: The inventory service back-end
    As a E-Commerce Website
    I need a RESTful inventory service
    So that I can keep track of all my inventories

Background:
    Given the following inventories
        | id   | count    | restock_level | condition | reorder_point |
        | 101  | 1000     | 100           | new       | 10            |
        | 102  | 500      | 30            | open-box  | 5             |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Get one Inventory
    When I visit the "Home Page"
    And I set the "Id" to "102"
    And I press the "Retrieve" button
    Then I should see "open-box" in the "Condition" field

Scenario: Create a Pet
    When I visit the "Home Page"
    And I set the "Id" to "103"
    And I set the "Count" to "1000"
    And I set the "restock_level" to "300"
    And I set the "reorder_point" to "100"
    And I set the "Condition" to "new"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all inventories
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "101" in the results
    And I should see "102" in the results
    And I should see "open-box" in the results

Scenario: Delete one Inventory
    When I visit the "Home Page"
    And I set the "Id" to "102"
    And I press the "Delete" button
    And I press the "Search" button
    Then I should not see "open-box" in the results
