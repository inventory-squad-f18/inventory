"""
    This module holds the model for our application
"""

class DataValidationError(Exception):
    """ Used for an data validation errors when getting object from JSON """
    pass

class Inventory(object):
    data = []


    def __init__(self, id, data):
        if not isinstance(id, int):
            raise DataValidationError("Invalid data: expected int in id, received " + type(id))
        if not isinstance(data, tuple):
            raise DataValidationError("Invalid data: expected tuple in data, received " + type(data))
        if len(data) != 4:
            raise DataValidationError("Expected 4 fields: count:int, restock-level:int, reorder-point:int, condition:string(new, open-box, used)")
        if not isinstance(data[0], int):
            raise DataValidationError("Invalid data: expected int in data[0], received " + type(data[0]))
        if not isinstance(data[1], int):
            raise DataValidationError("Invalid data: expected int in data[0], received " + type(data[1]))
        if not isinstance(data[2], int):
            raise DataValidationError("Invalid data: expected int in data[0], received " + type(data[0]))
        if data[2] >= data[1]:
            raise DataValidationError("Invalid data: expected ordering: data[2] < data[1]")
        if data[3] not in ["new", "open-box", "used"]:
            raise DataValidationError("Invalid data: expected value of data[3] is 'new' or 'open-box' or 'used'")
        self.id = id
        self.data = data

    def save(self):
        """
        Saves a Pet to the data store
        """
        # if id is duplicate?, if needs update
        Inventory.data.append(self)


    def to_json(self):
        """ serializes an inventory item into an dictionary """
        return {"id": self.id, "count": self.data[0], "restock-level": self.data[1], "reorder-point": self.data[2], "condition": self.data[3]}


    def from_json(self,json_val):
        """ deserializes inventory item from an dictionary """
        if not isinstance(json_val, dict):
            raise DataValidationError("Invalid data: expected dict, received " + type(json_val))
        try:
            self.data = (json_val['count'], json_val['restock-level'], json_val['reorder-point'], json_val['condition'])
        except KeyError as error:
            raise DataValidationError("Invalid data: missing " + error.args[0])
        return 
    
    @classmethod
    def find(cls, inventory_id):
        """ Finds a inventory by it's ID """
        print "cls.data ",cls,cls.data
        if not cls.data:
            return None
        inventory = [inventory for inventory in cls.data if inventory.id == inventory_id]
        if inventory:
            return inventory[0]
        return None


