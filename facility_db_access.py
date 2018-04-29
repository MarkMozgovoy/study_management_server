import boto3
from facility import Facility
from equipment_db_access import loadEquipmentList

dynamodb = boto3.resource('dynamodb')
FacilityTable = dynamodb.Table('Facility')

#CRUD functions that read/write to dynamo
def createFacility(facilityData):
    f = Facility()
    f.name = facilityData["name"]
    if "equipmentList" in facilityData:
        f.equipmentList = loadEquipmentList(facilityData["equipmentList"])
    FacilityTable.put_item(Item=f.toDynamo())
    return f

def getFacility(facilityId):
    response = FacilityTable.get_item(Key={"facilityId":facilityId})
    facilityData = response["Item"]
    return loadFacility(facilityData)

def getAllFacilities():
    response = FacilityTable.scan()
    facilityListData = response["Items"]
    return loadFacilityList(facilityListData)

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
        f.equipmentList = loadEquipmentList(facilityData["equipmentList"])
    return f

def loadFacilityList(facilityListData):
    """Returns a list of Facility objects for the given data"""
    #facilityListData can be a list of facilityIds (str) or facilityData (dict)
    fl = []
    for f in facilityListData:
        if type(f)==str:
            fl.append(getFacility(f))
        else: #type(f)==dict
            fl.append(loadFacility(f))
    return fl
