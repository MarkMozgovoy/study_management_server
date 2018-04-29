import boto3
from study import Study
from equipment_db_access import loadEquipmentList
from deployment_db_access import loadDeploymentList

dynamodb = boto3.resource('dynamodb')
StudyTable = dynamodb.Table('Study')

#CRUD functions that read/write to dynamo
def createStudy(studyData):
    s = Study()
    s.name = studyData["name"]
    if "description" in studyData:
        s.description = studyData["description"]
    if "equipmentList" in studyData:
        s.equipmentList = loadEquipmentList(studyData["equipmentList"])
    StudyTable.put_item(Item=s.toDynamo())
    return s

def getStudy(studyId):
    response = StudyTable.get_item(Key={"studyId":studyId})
    studyData = response["Item"]
    return loadStudy(studyData)

#Helper functions to convert lists/dicts into Study objects
def loadStudy(studyData):
    """Returns a Study object for the given data"""
    s = Study()
    s.studyId = studyData["studyId"]
    s.name = studyData["name"]
    if "description" in studyData:
        s.description = studyData["description"]
    s.status = studyData["status"]
    s.dateCreated = studyData["dateCreated"]
    s.dateModified = studyData["dateModified"]
    s.archived = studyData["archived"]
    if "deploymentList" in studyData:
        s.deploymentList = loadDeploymentList(studyData["deploymentList"])
    if "equipmentList" in studyData:
        s.equipmentList = loadEquipmentList(studyData["equipmentList"])
    return s
