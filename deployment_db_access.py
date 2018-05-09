from decimal import Decimal
from deployment import Deployment
import facility_db_access
import study_db_access
import errors

##CRUD functions that read/write to dynamo
def createDeployment(studyId, deploymentData):
    #check that deploymentData is valid
    if not ("name" in deploymentData and type(deploymentData["name"])==str and len(deploymentData["name"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'name' (type=str and length>0)")
    if not ("goalSampleSize" in deploymentData and type(deploymentData["goalSampleSize"]) in [int, Decimal] and deploymentData["goalSampleSize"]>0):
        raise errors.BadRequestError("Deployment must have attribute 'goalSampleSize' (type=int and value>0)")
    if not ("facility" in deploymentData and type(deploymentData["facility"]) in [str, dict] and len(deploymentData["facility"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'facility' (type=str or dict and length>0)")
    #construct the deployment
    d = Deployment()
    d.name = deploymentData["name"]
    if "description" in deploymentData:
        d.description = deploymentData["description"]
    d.goalSampleSize = int(deploymentData["goalSampleSize"])
    d.facility = facility_db_access.loadFacility(deploymentData["facility"])
    #create the deployment (by updating its parent study)
    return study_db_access.createDeploymentForStudy(studyId, d)

def getDeployment(studyId, deploymentId):
    for deployment in getAllDeployments(studyId):
        if deployment.deploymentId==deploymentId:
            return deployment
    return {}

def getAllDeployments(studyId):
    study = study_db_access.getStudy(studyId)
    return study.deploymentList

def updateDeployment(studyId, deploymentId, deploymentData):
    oldDeployment = getDeployment(studyId, deploymentId)
    newDeployment = loadDeployment(deploymentData)
    #check that the deployment can be updated
    if not (oldDeployment.deploymentId==newDeployment.deploymentId):
        raise errors.BadRequestError("deploymentId of the deployment to be updated must mach the deploymentId of the endpoint")
    if not (oldDeployment.dateModified==newDeployment.dateModified):
        raise errors.BadRequestError("dateModifed on the deployment to be updated does not match the dateModified in the database.")
    if not (newDeployment.status in ["CREATED", "DESIGNED", "DEPLOYED", "PAUSED", "TERMINATED"]):
        raise errors.BadRequestError("status must be CREATED, DESIGNED, DEPLOYED, PAUSED, or TERMINATED")
    #The archived flag can always be updated regardless of status
    oldDeployment.archived = newDeployment.archived
    if (oldDeployment.status=="CREATED"):
        if not (newDeployment.status in ["CREATED", "DESIGNED", "TERMINATED"]):
            raise errors.BadRequestError("status of a CREATED deployment can only be updated to DESIGNED or TERMINATED")
        oldDeployment.name = newDeployment.name
        oldDeployment.description = newDeployment.description
        oldDeployment.goalSampleSize = newDeployment.goalSampleSize
        oldDeployment.facility = newDeployment.facility
    if (oldDeployment.status=="DESIGNED"):
        if not (newDeployment.status in ["DESIGNED", "DEPLOYED", "TERMINATED"]):
            raise errors.BadRequestError("status of a DESIGNED deployment can only be updated to DEPLOYED or TERMINATED")
    if (oldDeployment.status=="DEPLOYED"):
        if not (newDeployment.status in ["DEPLOYED", "PAUSED", "TERMINATED"]):
            raise errors.BadRequestError("status of a DEPLOYED deployment can only be updated to PAUSED or TERMINATED")
        if study_db_access.getStudy(studyId).status=="DEPLOYED":
            oldDeployment.currentSampleSize = newDeployment.currentSampleSize
    if (oldDeployment.status=="PAUSED"):
        if not (newDeployment.status in ["DEPLOYED", "PAUSED", "TERMINATED"]):
            raise errors.BadRequestError("status of a PAUSED study can only be updated to DEPLOYED or TERMINATED")
    if (oldDeployment.status=="TERMINATED"):
        if not (newDeployment.status=="TERMINATED"):
            raise errors.BadRequestError("Cannot change the status of a TERMINATED study")
    oldDeployment.status = newDeployment.status
    #if the goalSampleSize has been reached, automatically pause the deployment
    if (oldDeployment.currentSampleSize>=oldDeployment.goalSampleSize and oldDeployment.status not in ["PAUSED", "TERMINATED"]):
        oldDeployment.status = "PAUSED"
    oldDeployment.modifyDate()
    return study_db_access.updateDeploymentForStudy(studyId, oldDeployment)

#Helper functions to convert lists/dicts into Deployment objects
def loadDeployment(deploymentData):
    """Returns a Deployment object for the given data"""
    #check that the deploymentData is valid
    if not ("deploymentId" in deploymentData and type(deploymentData["deploymentId"])==str and len(deploymentData["deploymentId"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'deploymentId' (type=str and length>0)")
    if not ("name" in deploymentData and type(deploymentData["name"])==str and len(deploymentData["name"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'name' (type=str and length>0)")
    if not ("status" in deploymentData and type(deploymentData["status"])==str and len(deploymentData["status"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'status' (type=str and length>0)")
    if not ("dateCreated" in deploymentData and type(deploymentData["dateCreated"])==str and len(deploymentData["dateCreated"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'dateCreated' (type=str and length>0)")
    if not ("dateModified" in deploymentData and type(deploymentData["dateModified"])==str and len(deploymentData["dateModified"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'dateCreated' (type=str and length>0)")
    if not ("archived" in deploymentData and type(deploymentData["archived"])==bool):
        raise errors.BadRequestError("Deployment must have attribute 'archived' (type=bool)")
    if not ("goalSampleSize" in deploymentData and type(deploymentData["goalSampleSize"]) in [int, Decimal] and deploymentData["goalSampleSize"]>0):
        raise errors.BadRequestError("Deployment must have attribute 'goalSampleSize' (type=int and value>0)")
    if not ("currentSampleSize" in deploymentData and type(deploymentData["currentSampleSize"]) in [int, Decimal] and deploymentData["currentSampleSize"]>=0):
        raise errors.BadRequestError("Deployment must have attribute 'currentSampleSize' (type=int and value>=0)")
    if not ("facility" in deploymentData and type(deploymentData["facility"]) in [str, dict] and len(deploymentData["facility"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'facility' (type=str or dict and length>0)")
    #construct the deployment
    d = Deployment()
    d.deploymentId = deploymentData["deploymentId"]
    d.name = deploymentData["name"]
    if "description" in deploymentData:
        d.description = deploymentData["description"]
    d.status = deploymentData["status"]
    d.dateCreated = deploymentData["dateCreated"]
    d.dateModified = deploymentData["dateModified"]
    d.archived = deploymentData["archived"]
    d.goalSampleSize = int(deploymentData["goalSampleSize"])
    d.currentSampleSize = int(deploymentData["currentSampleSize"])
    d.facility = facility_db_access.loadFacility(deploymentData["facility"])
    return d

def loadDeploymentList(deploymentListData):
    """Returns a list of Deployment objects for the given data"""
    #deploymentListData will always be a list of deploymentData (dict)
    dl = []
    for d in deploymentListData:
        dl.append(loadDeployment(d))
    return dl
