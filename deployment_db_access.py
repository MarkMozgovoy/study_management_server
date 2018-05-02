from deployment import Deployment
import facility_db_access
import study_db_access
import errors

##CRUD functions that read/write to dynamo
def createDeploymentForStudy(studyId, deploymentData):
    #check that a deployment can be created for the study
    s = study_db_access.getStudy(studyId)
    if s.status=="TERMINATED" or s.status=="CREATED":
        raise errors.BadRequestError("Unable to create deployment for "+s.status+" studies")
    if not (s.status=="DESIGNED" or s.status=="DEPLOYED" or s.status=="PAUSED"):
        raise errors.APIError("Study has unknown status type")
    #check that deploymentData is valid
    if not ("name" in deploymentData and type(deploymentData["name"])==str and len(deploymentData["name"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'name' (type=str and length>0)")
    if not ("goalSampleSize" in deploymentData and type(deploymentData["goalSampleSize"])==int and deploymentData["goalSampleSize"]>0):
        raise errors.BadRequestError("Deployment must have attribute 'goalSampleSize' (type=int and value>0)")
    if not ("facility" in deploymentData and type(deploymentData["facility"])==str and len(deploymentData["facility"])>0):
        raise errors.BadRequestError("Deployment must have attribute 'facility' (type=str and length>0)")
    facility = facility_db_access.getFacility(deploymentData["facility"])
    if not facility_db_access.facilityContainsAllEquipment(facility, s.equipmentList):
        raise errors.BadRequestError("Deployment 'facility' must have all of the equpiment required by its Study")
    #construct the deployment
    d = Deployment()
    d.name = deploymentData["name"]
    if "description" in deploymentData:
        d.description = deploymentData["description"]
    d.goalSampleSize = int(deploymentData["goalSampleSize"])
    d.facility = facility_db_access.loadFacility(deploymentData["facility"])
    #create the deployment (by updating its parent study)
    s.deploymentList.append(d)
    s.modifyDate(d.dateModified)
    study_db_access.updateStudy(s)
    return d

def getDeploymentForStudy(studyId, deploymentId):
    for deployment in getAllDeploymentsForStudy(studyId):
        if deployment.deploymentId==deploymentId:
            return deployment
    return {}

def getAllDeploymentsForStudy(studyId):
    study = study_db_access.getStudy(studyId)
    return study.deploymentList

#Helper functions to convert lists/dicts into Deployment objects
def loadDeployment(deploymentData):
    """Returns a Deployment object for the given data"""
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
