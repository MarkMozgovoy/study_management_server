import json

class DBHelper:
    def getIdOrDictAsChild(self, forDynamo):
        """Return object id if object has its own table in Dynamo and forDynamo==true, else return dict"""
        return self.__dict__
    def toDynamo(self):
        return trim(expand(self.__dict__, True))

def toJson(obj):
    return json.dumps(expand(obj, False))

def expand(obj, forDynamo):
    """Returns a copy of the object with its sub-objects expanded"""
    copy = None
    if type(obj)==list:
        copy = []
        for i in obj:
            copy.append(expand(i, forDynamo))
    elif type(obj)==dict:
        copy = {}
        for k,v in obj.items():
            copy[k]=expand(v, forDynamo)
    elif isinstance(obj, DBHelper):
        copy = expand(obj.getIdOrDictAsChild(forDynamo), forDynamo)
    else:
        copy = obj
    return copy

def trim(obj):
    """Returns a copy of the object with empty values removed"""
    copy = None
    if type(obj)==list:
        copy = []
        for i in obj:
            ti = trim(i)
            if not shouldTrim(ti):
                copy.append(ti)
    elif type(obj)==dict:
        copy = {}
        for k,v in obj.items():
            tv = trim(v)
            if not shouldTrim(tv):
                copy[k] = tv
    else:
        if not shouldTrim(obj):
            copy = obj
    return copy

def shouldTrim(obj):
    if obj==None:
        return True
    if type(obj)==str and len(obj)==0:
        return True
    if type(obj)==dict and len(obj)==0:
        return True
    if type(obj)==list and len(obj)==0:
        return True
    return False
