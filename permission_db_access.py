import boto3
from boto3.dynamodb.conditions import Key
import study_db_access

dynamodb = boto3.resource('dynamodb')
PermissionTable = dynamodb.Table('Permission')

#CRUD functions that read/write to dynamo
def createOwnerForStudy(userId, studyId):
    return createUserPermissionForStudy(userId, studyId, "OWNER")

def createAdminForStudy(userId, studyId):
    if userHasPermissionForStudy(userId, studyId):
        return getUserPermissionForStudy(userId, studyId)
    else:
        return createUserPermissionForStudy(userId, studyId, "ADMIN")

def createUserPermissionForStudy(userId, studyId, permission):
    permission1 = {
        "userOrStudyId": userId,
        "studyOrUserId": studyId,
        "role": permission
    }
    permission2 = {
        "userOrStudyId": studyId,
        "studyOrUserId": userId,
        "role": permission
    }
    PermissionTable.put_item(Item=permission1)
    PermissionTable.put_item(Item=permission2)
    userPermission = {
        "userId": userId,
        "studyId": studyId,
        "role": permission
    }
    return userPermission

def userHasPermissionForStudy(userId, studyId):
    response = PermissionTable.query(
        KeyConditionExpression = Key("userOrStudyId").eq(userId) & Key("studyOrUserId").eq(studyId)
    )
    return len(response["Items"])>0

def getUserPermissionForStudy(userId, studyId):
    response = PermissionTable.query(
        KeyConditionExpression = Key("userOrStudyId").eq(userId) & Key("studyOrUserId").eq(studyId)
    )
    permission = response["Items"][0]
    userPermission = {
        "userId": permission["userOrStudyId"],
        "studyId": permission["studyOrUserId"],
        "role": permission["role"]
    }
    return userPermission

def getStudiesForUser(userId):
    response = PermissionTable.query(
        KeyConditionExpression = Key("userOrStudyId").eq(userId)
    )
    permissionData = response["Items"]
    studyList = []
    for permission in permissionData:
        studyId = permission["studyOrUserId"]
        studyList.append(study_db_access.getStudy(studyId))
    return studyList

def getPermissionsForStudy(studyId):
    response = PermissionTable.query(
        KeyConditionExpression = Key("userOrStudyId").eq(studyId)
    )
    permissionData = response["Items"]
    userPermissionList = []
    for permission in permissionData:
        userId = permission["studyOrUserId"]
        role = permission["role"]
        userPermission = {
            "userId": userId,
            "role": role
        }
        userPermissionList.append(userPermission)
    return userPermissionList
