Feature: The inventory service back-end
    As a E-Commerce Website
    I need a RESTful inventory service
    So that I can keep track of all my inventories

Background:
    Given the following inventories
        | id   | count    | restock-level | condition | reorder-point |
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


