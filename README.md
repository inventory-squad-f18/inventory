# inventory
[![Build Status](https://travis-ci.org/inventory-squad-f18/inventory.svg?branch=master)](https://travis-ci.org/inventory-squad-f18/inventory)
[![codecov](https://codecov.io/gh/inventory-squad-f18/inventory/branch/master/graph/badge.svg)](https://codecov.io/gh/inventory-squad-f18/inventory)

The inventory API provides service to keep track of resources in warehouse.

* [Description](#description)

## Description
Inventory is a Microservice built using 12 factor standards and accessible via RESTful API calls. Inventory service provides access to inventory of e-commerce website by RESTful API calls to Create, Read, Update, Delete, List and Query inventory.
Inventory API provides service to keep track of resrouces in warehouse. It provides count of each inventory item in warehouse and also holds it's condition i.e. whether it is `'new', 'old' or 'open-box'`. Service also maintains the re-order point and restock level of items so that user can re-order item so that the count reaches restock level.
The API is RESTful and returns result in JSON format. For futher details about JSON Format click [here](#json-format)

## JSON Format
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| publisher | String | Yes | Name of work's publisher |
