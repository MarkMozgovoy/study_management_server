from dbhelper import DBHelper
from uuid import uuid4

class Equipment(DBHelper):
    def __init__(self):
        self.equipmentId = "EQUIPMENT:" + str(uuid4())
        self.name = ""
        self.abbreviation = ""
    def getIdOrDictAsChild(self, forDynamo):
        """Return object id if object has its own table in Dynamo and forDynamo==true, else return dict"""
        if forDynamo:
            return self.equipmentId
        return self.__dict__
    def __eq__(self, other):
        return (
            self.equipmentId==other.equipmentId and
            self.name==other.name and
            self.abbreviation==other.abbreviation
        )
