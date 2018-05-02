from deployment import Deployment
import facility_db_access
import study_db_access

##CRUD functions that read/write to dynamo
def createDeploymentForStudy(studyId, deploymentData):
    #check that a deployment can be created for the study
    s = study_db_access.getStudy(studyId)
    if s.status=="TERMINATED":
        return "ERROR: unable to create deployment for TERMINATED study", 400
    if s.status=="CREATED":
        return "ERROR: unable to create deployment for CREATED study", 400
    if not (s.status=="DESIGNED" or s.status=="DEPLOYED" or s.status=="PAUSED"):
        return "ERROR: study has unknown status", 500
    #construct the deployment
    d = Deployment()
    d.name = deploymentData["name"]
    if "description" in deploymentData:
        d.description = deploymentData["description"]
    d.goalSampleSize = deploymentData["goalSampleSize"]
    d.facility = facility_db_access.loadFacility(deploymentData["facility"])
    if not facility_db_access.facilityContainsAllEquipment(d.facility, s.equipmentList):
        return "ERROR: unable to create deployment. Facility does not have the required equipment.", 400
    #update the study
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
