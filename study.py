from uuid import uuid4
from datetime import datetime
from dbhelper import DBHelper

class Study(DBHelper):
    def __init__(self):
        self.studyId = "STUDY:" + str(uuid4())
        self.name = ""
        self.description = ""
        self.status = "CREATED"
        self.dateCreated = str(datetime.now())
        self.dateModified = self.dateCreated
        self.archived = False
        self.deploymentList = []
        self.equipmentList = []
    def modifyDate(self):
        self.dateModified = str(datetime.now())
    def getIdOrDictAsChild(self, forDynamo):
        """Return object id if object has its own table in Dynamo and forDynamo==true, else return dict"""
        if forDynamo:
            return self.studyId
        return self.__dict__
