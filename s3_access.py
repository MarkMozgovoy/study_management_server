import boto3
import botocore
import errors
import study_db_access


BUCKET_NAME = "edu-stjohns-cus1166-study-management"
s3 = boto3.client("s3")

def uploadFile(studyId, file):
    study = study_db_access.getStudy(studyId)
    if not study.status == "CREATED":
        raise errors.BadRequestError("Files can only uploaded for CREATED studies")
    fileName =file.filename
    key = studyId+fileName
    s3.upload_fileobj(file, BUCKET_NAME, key)
    study.resourceList.append(fileName)
    study_db_access.updateStudy(studyId, study.toDynamo())
    return fileName

def downloadFile(studyId, fileName):
    study = study_db_access.getStudy(studyId)
    if fileName not in study.resourceList:
        raise errors.BadRequestError("No file named " +fileName+ " for study " + studyId)
    key = studyId+fileName
    file = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return file
