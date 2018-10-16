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
        try:
            Inventory.validate_data(data)
        except:
            raise
        self.id = id
        self.data = data


    @classmethod
    def validate_data(cls, data):
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


    def save(self):
        """
        Saves a Inventory to the data store
        """
        # if id is duplicate?, if needs update
        #Inventory.data.append(self)

        id_list = [item.id for item in Inventory.data]
        if self.id not in id_list:
            Inventory.data.append(self)
        else:
            for i in range(len(Inventory.data)):
                if Inventory.data[i].id == self.id:
                    Inventory.data[i] = self
                    break

    def delete(self):
        """ Removes a Invengory from the data store """
        Inventory.data.remove(self)


    def to_json(self):
        """ serializes an inventory item into an dictionary """
        return {"id": self.id, "count": self.data[0], "restock-level": self.data[1], "reorder-point": self.data[2], "condition": self.data[3]}


    def from_json(self,json_val):
        """ deserializes inventory item from an dictionary """
        if not isinstance(json_val, dict):
            raise DataValidationError("Invalid data: expected dict, received " + type(json_val))
        try:
            data = (json_val['count'], json_val['restock-level'], json_val['reorder-point'], json_val['condition'])
            Inventory.validate_data(data)
            self.data = data
        except DataValidationError:
            raise
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

    @classmethod
    def find_by_condition(cls, condition):
        """ Finds a inventory by it's ID """
        print "cls.data ",cls,cls.data
        if condition not in ["new", "open-box", "used"]:
            raise DataValidationError("Invalid data: expected value of condition is 'new' or 'open-box' or 'used'")
        if not cls.data:
            return None
        inventory = [inventory for inventory in cls.data if inventory.data[3] == condition]
        return inventory

    @classmethod
    def all(cls):
        """ Returns all of the Inventorys in the database """
        return [inventory for inventory in cls.data]
