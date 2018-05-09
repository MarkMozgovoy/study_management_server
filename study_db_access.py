import boto3
from study import Study
import equipment_db_access
import facility_db_access
import deployment_db_access
import errors

dynamodb = boto3.resource('dynamodb')
StudyTable = dynamodb.Table('Study')

#CRUD functions that read/write to dynamo
def createStudy(studyData):
    #check that the studyData is valid
    if not ("name" in studyData and type(studyData["name"])==str and len(studyData["name"])>0):
        raise errors.BadRequestError("Study must have attribute 'name' (type=str and length>0)")
    #construct the study
    s = Study()
    s.name = studyData["name"]
    if "description" in studyData:
        s.description = studyData["description"]
    if "equipmentList" in studyData:
        s.equipmentList = equipment_db_access.loadEquipmentList(studyData["equipmentList"])
    #create the study
    StudyTable.put_item(Item=s.toDynamo())
    return s

def getStudy(studyId):
    response = StudyTable.get_item(Key={"studyId":studyId})
    studyData = response["Item"]
    return loadStudy(studyData)

def updateStudy(study):
    StudyTable.put_item(Item=study.toDynamo())
    return study

def createDeploymentForStudy(studyId, deployment):
    s = getStudy(studyId)
    if s.status=="TERMINATED" or s.status=="CREATED":
        raise errors.BadRequestError("Unable to create deployment for "+s.status+" studies")
    if not (s.status=="DESIGNED" or s.status=="DEPLOYED" or s.status=="PAUSED"):
        raise errors.APIError("Study has unknown status type")
    if not facility_db_access.facilityContainsAllEquipment(deployment.facility, s.equipmentList):
        raise errors.BadRequestError("Deployment 'facility' must have all of the equpiment required by its Study")
    s.deploymentList.append(deployment)
    s.modifyDate(deployment.dateModified)
    StudyTable.put_item(Item=s.toDynamo())
    return deployment

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
        s.deploymentList = deployment_db_access.loadDeploymentList(studyData["deploymentList"])
    if "equipmentList" in studyData:
        s.equipmentList = equipment_db_access.loadEquipmentList(studyData["equipmentList"])
    return s
