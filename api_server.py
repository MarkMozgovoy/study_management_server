from flask import Flask, request
import equipment_db_access
import facility_db_access
import permission_db_access
import study_db_access
import deployment_db_access
import errors
from dbhelper import toJson
import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

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
    validateUser()
    studyData = request.get_json()
    study = study_db_access.createStudy(studyData)
    permission_db_access.createOwnerForStudy(getUserId(), study.studyId)
    return toJson(study)

@app.route('/studies', methods=['GET'])
def getStudiesForUser():
    validateUser()
    studyList = permission_db_access.getStudiesForUser(getUserId())
    return toJson(studyList)

@app.route('/studies/<studyId>', methods=['GET'])
def getStudy(studyId):
    validateUser(studyId)
    study = study_db_access.getStudy(studyId)
    return toJson(study)

@app.route('/studies/<studyId>/facilities', methods=['GET'])
def getFacilitiesForStudy(studyId):
    validateUser(studyId)
    facilityList = facility_db_access.getFacilitiesForStudy(studyId)
    return toJson(facilityList)

@app.route('/studies/<studyId>/permissions', methods=['POST'])
def createPermissionForStudy(studyId):
    validateUser(studyId)
    permissionData = request.get_json()
    if not ("userId" in permissionData and type(permissionData["userId"])==str and len(permissionData["userId"])>0):
        raise errors.BadRequestError("Permission must have attribute 'userId' (type=str and length>0)")
    userId = permissionData["userId"]
    userPermission = permission_db_access.createAdminForStudy(userId, studyId)
    return toJson(userPermission)

@app.route('/studies/<studyId>/permissions', methods=['GET'])
def getPermissionsForStudy(studyId):
    validateUser(studyId)
    userPermissionList = permission_db_access.getPermissionsForStudy(studyId)
    return toJson(userPermissionList)

@app.route('/studies/<studyId>/deployments', methods=['GET'])
def getAllDeploymentsForStudy(studyId):
    validateUser(studyId)
    deploymentList = deployment_db_access.getAllDeploymentsForStudy(studyId)
    return toJson(deploymentList)

@app.route('/studies/<studyId>/deployments', methods=['POST'])
def createDeploymentForStudy(studyId):
    validateUser(studyId)
    deploymentData = request.get_json()
    deployment = deployment_db_access.createDeploymentForStudy(studyId, deploymentData)
    return toJson(deployment)

@app.route('/studies/<studyId>/deployments/<deploymentId>', methods=['GET'])
def getDeploymentForStudy(studyId, deploymentId):
    validateUser(studyId)
    deployment = deployment_db_access.getDeploymentForStudy(studyId, deploymentId)
    return toJson(deployment)

#Authentication helper functions
def validateUser(studyId=None, token):
    pems_dict = {
        'kid1': 'pem1',
        'kid2': 'pem2'
    }

    kid = jwt.get_unverified_header(token)['kid']
    pem = pems_dict.get(kid, None)

    if pem is None:
        print 'kid false'
        return False

    try:
        decoded_token = jwt.decode(token, pem, algorithms=['RS256'])
        iss = 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_qI2amo5xv'
        if decoded_token['iss'] != iss:
            print 'iss false'
            return False
        elif decoded_token['token_use'] != 'access':
            print 'access false'
            return False
        return True
    except Exception:
        return False
    if studyId!=None:
        if not permission_db_access.userHasPermissionForStudy(getUserId(), studyId):
            raise errors.ForbiddenError("User does not have permission to access " + studyId)
    return True

def getUserId():
    userId = jwt.GetUser.Username
    return userId

#Error Handling
@app.errorhandler(404)
def handleNotFoundEror(e):
    return toJson({"error":type(e).__name__, "status":404, "message":str(e)}), 404

@app.errorhandler(500)
def handleInternalServerError(e):
    return toJson({"error":type(e).__name__, "status":500, "message":"Internal Server Error"}), 500

@app.errorhandler(errors.APIError)
def handleAPIError(e):
    return toJson({"error":type(e).__name__, "status":e.getStatusCode(), "message":str(e)}), e.getStatusCode()

#Developing locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
