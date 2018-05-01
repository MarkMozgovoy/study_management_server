from flask import Flask, request
import equipment_db_access
import facility_db_access
import permission_db_access
import study_db_access
import deployment_db_access
from dbhelper import toJson

app = Flask(__name__)

invalidUserTokenMessage = "Invalid user token"
userNotAuthorizedMessage = "User is not authorized to perform the requested action"

@app.route('/')
def root():
    return 'You have hit the Study Management Server root endpoint!'

#Equipment Endpoints
@app.route('/equipment/<equipmentId>', methods=['GET'])
def getEquipment(equipmentId):
    equipment = equipment_db_access.getEquipment(equipmentId)
    return toJson(equipment)

@app.route('/equipment', methods=['GET'])
def getAllEquipment():
    equipmentList = equipment_db_access.getAllEquipment()
    return toJson(equipmentList)

#Facility endpoints
@app.route('/facilities/<facilityId>', methods=['GET'])
def getFacility(facilityId):
    facility = facility_db_access.getFacility(facilityId)
    return toJson(facility)

@app.route('/facilities', methods=['GET'])
def getAllFacilities():
    facilityList = facility_db_access.getAllFacilities()
    return toJson(facilityList)

#Study endpoints
@app.route('/studies', methods=['POST'])
def createStudy():
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    studyData = request.get_json()
    study = study_db_access.createStudy(studyData)
    permission_db_access.createOwnerForStudy(getUserId(), study.studyId)
    return toJson(study)

@app.route('/studies', methods=['GET'])
def getStudiesForUser():
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    studyList = permission_db_access.getStudiesForUser(getUserId())
    return toJson(studyList)

@app.route('/studies/<studyId>', methods=['GET'])
def getStudy(studyId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    study = study_db_access.getStudy(studyId)
    return toJson(study)

@app.route('/studies/<studyId>/facilities', methods=['GET'])
def getFacilitiesForStudy(studyId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    facilityList = facility_db_access.getFacilitiesForStudy(studyId)
    return toJson(facilityList)

@app.route('/studies/<studyId>/permissions', methods=['POST'])
def createPermissionForStudy(studyId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    userId = request.get_json()["userId"]
    userPermission = permission_db_access.createAdminForStudy(userId, studyId)
    return toJson(userPermission)

@app.route('/studies/<studyId>/permissions', methods=['GET'])
def getPermissionsForStudy(studyId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    userPermissionList = permission_db_access.getPermissionsForStudy(studyId)
    return toJson(userPermissionList)

@app.route('/studies/<studyId>/deployments', methods=['GET'])
def getAllDeploymentsForStudy(studyId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    deploymentList = deployment_db_access.getAllDeploymentsForStudy(studyId)
    return toJson(deploymentList)

@app.route('/studies/<studyId>/deployments/<deploymentId>', methods=['GET'])
def getDeploymentForStudy(studyId, deploymentId):
    if not userTokenIsValid():
        return invalidUserTokenMessage, 401
    if not userHasPermission(studyId):
        return userNotAuthorizedMessage, 401
    deployment = deployment_db_access.getDeploymentForStudy(studyId, deploymentId)
    return toJson(deployment)

#Authentication helper functions
def userTokenIsValid():
    #TODO: validate the signature and expiration time of the user token
    return True

def userHasPermission(studyId):
    return permission_db_access.userHasPermissionForStudy(getUserId(), studyId)

def getUserId():
    #TODO: userId must be a unique and unmodifiable attribute of the user token
    return "USER:TEST_USER"

#Developing locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
