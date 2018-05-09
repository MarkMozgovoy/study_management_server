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

def updateStudy(studyId, studyData):
    oldStudy = getStudy(studyId)
    newStudy = loadStudy(studyData)
    #check that the study can be updated
    if not (oldStudy.studyId==newStudy.studyId):
        raise errors.BadRequestError("studyId of the study to be updated must mach the studyId of the endpoint")
    if not (oldStudy.dateModified==newStudy.dateModified):
        raise errors.BadRequestError("dateModifed on the study to be updated does not match the dateModified in the database.")
    if not (newStudy.status in ["CREATED", "DESIGNED", "DEPLOYED", "PAUSED", "TERMINATED"]):
        raise errors.BadRequestError("status must be CREATED, DESIGNED, DEPLOYED, PAUSED, or TERMINATED")
    #The archived flag can always be updated regardless of status
    oldStudy.archived = newStudy.archived
    if (oldStudy.status=="CREATED"):
        if not (newStudy.status in ["CREATED", "DESIGNED", "TERMINATED"]):
            raise errors.BadRequest("status of a CREATED study can only be updated to DESIGNED or TERMINATED")
        oldStudy.name = newStudy.name
        oldStudy.description = newStudy.description
        oldStudy.equipmentList = newStudy.equipmentList
    if (oldStudy.status=="DESIGNED"):
        if not (newStudy.status in ["DESIGNED", "DEPLOYED", "TERMINATED"]):
            raise errors.BadRequest("status of a DESIGNED study can only be updated to DEPLOYED or TERMINATED")
    if (oldStudy.status=="DEPLOYED"):
        if not (newStudy.status in ["DEPLOYED", "PAUSED", "TERMINATED"]):
            raise errors.BadRequest("status of a DEPLOYED study can only be updated to PAUSED or TERMINATED")
    if (oldStudy.status=="PAUSED"):
        if not (newStudy.status in ["DEPLOYED", "PAUSED", "TERMINATED"]):
            raise errors.BadRequest("status of a PAUSED study can only be updated to DEPLOYED or TERMINATED")
    if (oldStudy.status=="TERMINATED"):
        if not (newStudy.status=="TERMINATED"):
            raise errors.BadRequest("Cannot change the status of a TERMINATED study")
    if (newStudy.status=="TERMINATED"):
        for d in oldStudy.deploymentList:
            if not d.status=="TERMINATED":
                d.status = "TERMINATED"
                d.modifyDate()
    oldStudy.status = newStudy.status
    oldStudy.modifyDate()
    StudyTable.put_item(Item=oldStudy.toDynamo())
    return oldStudy

def createDeploymentForStudy(studyId, deployment):
    s = getStudy(studyId)
    if not (s.status in ["DESIGNED", "DEPLOYED", "PAUSED"]):
        raise errors.APIError("Deployments can only be created for DESIGNED, DEPLOYED, and PAUSED studies")
    if not facility_db_access.facilityContainsAllEquipment(deployment.facility, s.equipmentList):
        raise errors.BadRequestError("Deployment 'facility' must have all of the equpiment required by its Study")
    s.deploymentList.append(deployment)
    s.modifyDate()
    StudyTable.put_item(Item=s.toDynamo())
    return deployment

#Helper functions to convert lists/dicts into Study objects
def loadStudy(studyData):
    """Returns a Study object for the given data"""
    #check that the studyData is valid
    if not ("studyId" in studyData and type(studyData["studyId"])==str and len(studyData["studyId"])>0):
        raise errors.BadRequestError("Study must have attribute 'studyId' (type=str and length>0)")
    if not ("name" in studyData and type(studyData["name"])==str and len(studyData["name"])>0):
        raise errors.BadRequestError("Study must have attribute 'name' (type=str and length>0)")
    if not ("status" in studyData and type(studyData["status"])==str and len(studyData["status"])>0):
        raise errors.BadRequestError("Study must have attribute 'status' (type=str and length>0)")
    if not ("dateCreated" in studyData and type(studyData["dateCreated"])==str and len(studyData["dateCreated"])>0):
        raise errors.BadRequestError("Study must have attribute 'dateCreated' (type=str and length>0)")
    if not ("archived" in studyData and type(studyData["archived"])==bool):
        raise errors.BadRequestError("Study must have attribute 'archived' (type=bool)")
    #construct the study
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
