# inventory
[![Build Status](https://travis-ci.org/inventory-squad-f18/inventory.svg?branch=master)](https://travis-ci.org/inventory-squad-f18/inventory)
[![codecov](https://codecov.io/gh/inventory-squad-f18/inventory/branch/master/graph/badge.svg)](https://codecov.io/gh/inventory-squad-f18/inventory)

The inventory API provides service to keep track of resources in warehouse.

* [Description](#description)
* [JSON Format](#json-format)
* [Get Inventories](#get-inventories)
* [Create Inventory Item](#create-inventory-item)
* [Update Inventory Item](#update-inventory-item)
* [Delete Inventory Item](#delete-inventory-item)
* [Reorder one inventory item](#reorder-one-inventory-item)
* [Reorder all inventory items](#reorder-all-inventory-items)

## Description
Inventory is a Microservice built using 12 factor standards and accessible via RESTful API calls. Inventory service provides access to inventory of e-commerce website by RESTful API calls to Create, Read, Update, Delete, List and Query inventory.
Inventory API provides service to keep track of resrouces in warehouse. It provides count of each inventory item in warehouse and also holds it's condition i.e. whether it is `'new', 'used' or 'open-box'`. Service also maintains the re-order point and restock level of items so that user can re-order item so that the count reaches restock level.
The API is RESTful and returns result in JSON format. For futher details about JSON Format click [here](#json-format)

## JSON Format
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | int | Yes | ID of the inventory item |
| count | int | Yes | Count of the item present in warehouse |
| reorder_point | int | Yes | If count falls below this value then it requires ordering to reach restock_level |
| restock_level | int | Yes | Point till which to reorder the item |
| condition | string in ('new', 'used', 'open-box') | Yes | Condition of the item |

## GET Inventories
Get call to `/inventory` allows to retrieve items from the inventory list. Following table defines the url, parameters and expected results of the call.

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory | GET | NA | list of all the inventory items |
| /api/inventory/\<int::inventory_id> | GET | NA | inventory represented by ID or 404 not found if it does not exists |
| /api/inventory | GET | condition in ('new', 'used', 'open-box') | list of inventory items in condition specified by parameter |

## Create Inventory Item
It allows to create new inventory item.

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory | POST | JSON {'id': \<int:id>, 'count': \<int:count>, 'restock_level': \<int:restock_level>, 'reorder_point': \<int:reorder_point>, 'condition': \<string:condition> } | list of all the inventory items |

## Update Inventory Item
It allows to update existing inventory item

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory/\<int::inventory_id> | PUT | JSON {'id': \<int:id>, 'count': \<int:count>, 'restock_level': \<int:restock_level>, 'reorder_point': \<int:reorder_point>, 'condition': \<string:condition> } | Updated inventory item |

## Delete Inventory Item
It allows to delete an inventory item

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory/\<int::inventory_id> | DELETE | NA | Empty response |


## Reorder one inventory item
It allows reordering single inventory item whose count is less than or equal to restock level

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory/\<int:inventory_id>/reorder | PUT | NA | Updated a specified inventory item |

## Reorder all inventory items
It allows reordering multiple inventory items whose count is less than or equal to restock level

| url | method | parameter | result |
|-----|--------|-----------|--------|
| /api/inventory/reorder | PUT | NA | Updated multiple inventory items |
