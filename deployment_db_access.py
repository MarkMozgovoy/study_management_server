from deployment import Deployment
from facility_db_access import loadFacility

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
    d.facility = loadFacility(deploymentData["facility"])
    return d

def loadDeploymentList(deploymentListData):
    """Returns a list of Deployment objects for the given data"""
    #deploymentListData will always be a list of deploymentData (dict)
    dl = []
    for d in deploymentListData:
        dl.append(loadDeployment(d))
    return dl
