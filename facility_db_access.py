import boto3
from facility import Facility
import equipment_db_access
import study_db_access
import errors

dynamodb = boto3.resource('dynamodb')
FacilityTable = dynamodb.Table('Facility')

#CRUD functions that read/write to dynamo
def createFacility(facilityData):
    #check that facilityData is valid
    if not ("name" in deploymentData and type(deploymentData["name"])==str and len(deploymentData["name"])>0):
        raise errors.BadRequestError("Facility must have attribute 'name' (type=str and length>0)")
    #construct the facility
    f = Facility()
    f.name = facilityData["name"]
    if "equipmentList" in facilityData:
        f.equipmentList = equipment_db_access.loadEquipmentList(facilityData["equipmentList"])
    #create the facility
    FacilityTable.put_item(Item=f.toDynamo())
    return f

def getFacility(facilityId):
    response = FacilityTable.get_item(Key={"facilityId":facilityId})
    try:
        facilityData = response["Item"]
    except KeyError:
        raise errors.APIError("No facility found for id: " + str(facilityId))
    return loadFacility(facilityData)

def getAllFacilities():
    response = FacilityTable.scan()
    facilityListData = response["Items"]
    return loadFacilityList(facilityListData)

def getFacilitiesForStudy(studyId):
    study = study_db_access.getStudy(studyId)
    studyEquipmentList = study.equipmentList
    allFacilities = getAllFacilities()
    facilityList = []
    for facility in allFacilities:
        if facilityContainsAllEquipment(facility, studyEquipmentList):
            facilityList.append(facility)
    return facilityList

#Helper functions to convert lists/dicts into Facility objects
def loadFacility(facilityData):
    """Returns a facility object for the given data"""
    #In case facilityData is just a string with the facilityId
    if type(facilityData)==str:
        return getFacility(facilityData)
    #Otherwise facilityData should be a dictionary as expected
    f = Facility()
    f.facilityId = facilityData["facilityId"]
    f.name = facilityData["name"]
    if "equipmentList" in facilityData:
        f.equipmentList = equipment_db_access.loadEquipmentList(facilityData["equipmentList"])
    return f

def loadFacilityList(facilityListData):
    """Returns a list of Facility objects for the given data"""
    #facilityListData can be a list of facilityIds (str), or facilityData (dict)
    fl = []
    for f in facilityListData:
        fl.append(loadFacility(f))
    return fl

#Other Helper functions
def facilityContainsAllEquipment(facility, studyEquipmentList):
    for se in studyEquipmentList:
        facilityContainsSE = False
        for fe in facility.equipmentList:
            if se.equipmentId == fe.equipmentId:
                facilityContainsSE = True
        if not facilityContainsSE:
            return False
    return True
