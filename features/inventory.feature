Feature: The inventory service back-end
    As a E-Commerce Website
    I need a RESTful inventory service
    So that I can keep track of all my inventories

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service" in the title
    And I should not see "404 Not Found"
