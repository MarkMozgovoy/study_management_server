from uuid import uuid4
from datetime import datetime
from dbhelper import DBHelper

class Deployment(DBHelper):
    def __init__(self):
        self.deploymentId = "DEPLOYMENT:" + str(uuid4())
        self.name = ""
        self.description = ""
        self.status = "CREATED"
        self.dateCreated = str(datetime.now())
        self.dateModified = self.dateCreated
        self.archived = False
        self.goalSampleSize = 100
        self.currentSampleSize = 0
        self.facility = None
    def modifyDate(self):
        self.dateModified = str(datetime.now())
