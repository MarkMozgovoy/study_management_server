from flask import Flask, request
import equipment_db_access
import facility_db_access
import permission_db_access
import study_db_access
from dbhelper import toJson

app = Flask(__name__)

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
    studyData = request.get_json()
    study = study_db_access.createStudy(studyData)
    permission_db_access.createOwnerForStudy(getUserId(), study.studyId)
    return toJson(study)

@app.route('/studies', methods=['GET'])
def getStudiesForUser():
    studyList = permission_db_access.getStudiesForUser(getUserId())
    return toJson(studyList)

@app.route('/studies/<studyId>', methods=['GET'])
def getStudy(studyId):
    study = study_db_access.getStudy(studyId)
    return toJson(study)

@app.route('/studies/<studyId>/facilities', methods=['GET'])
def getFacilitiesForStudy(studyId):
    facilityList = facility_db_access.getFacilitiesForStudy(studyId)
    return toJson(facilityList)

@app.route('/studies/<studyId>/permissions', methods=['GET'])
def getPermissionsForStudy(studyId):
    userPermissionList = permission_db_access.getUserPermissionsForStudy(studyId)
    return toJson(userPermissionList)

#Permissions endpoints
@app.route('/permissions', methods=['POST'])
def createAdminForStudy():
    permissionData = request.get_json()
    userPermission = permission_db_access.createAdminForStudy(permissionData)
    return toJson(userPermission)

#Helper functions
def getUserId():
    return "USER:TEST_USER"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
