import boto3
from equipment import Equipment
import errors

dynamodb = boto3.resource('dynamodb')
EquipmentTable = dynamodb.Table('Equipment')

#CRUD functions that read/write to dynamo
def createEquipment(equipmentData):
    #check that equipmentData is valid
    if not ("name" in equipmentData and type(equipmentData["name"])==str and len(equipmentData["name"])>0):
        raise errors.BadRequestError("Equipment must have attribute 'name' (type=str and length>0)")
    #construct the equipment
    e = Equipment()
    e.name = equipmentData["name"]
    if "abbreviation" in equipmentData:
        e.abbreviation = equipmentData["abbreviation"]
    #create the equipment
    EquipmentTable.put_item(Item=e.toDynamo())
    return e

def getEquipment(equipmentId):
    response = EquipmentTable.get_item(Key={"equipmentId": equipmentId})
    equipmentData = response["Item"]
    return loadEquipment(equipmentData)

def getAllEquipment():
    response = EquipmentTable.scan()
    equipmentListData = response["Items"]
    return loadEquipmentList(equipmentListData)

#Helper functions to convert lists/dicts into Equipment objects
def loadEquipment(equipmentData):
    """Returns an Equipment object for the given data"""
    e = Equipment()
    e.equipmentId = equipmentData["equipmentId"]
    e.name = equipmentData["name"]
    if "abbreviation" in equipmentData:
        e.abbreviation = equipmentData["abbreviation"]
    return e

def loadEquipmentList(equipmentListData):
    """Returns a list of Equipment objects for the given data"""
    #equipmentListData can be a list of equipentIds (str) or equipmentData (dict)
    el = []
    for e in equipmentListData:
        if type(e)==str:
            el.append(getEquipment(e))
        else: #type(e)==dict
            el.append(loadEquipment(e))
    return el
