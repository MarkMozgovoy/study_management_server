from uuid import uuid4
from dbhelper import DBHelper

class Facility(DBHelper):
    def __init__(self):
        self.facilityId = "FACILITY:" + str(uuid4())
        self.name = ""
        self.equipmentList = []
    def getIdOrDictAsChild(self, forDynamo):
        """Return object id if object has its own table in Dynamo and forDynamo==true, else return dict"""
        if forDynamo:
            return self.facilityId
        return self.__dict__
