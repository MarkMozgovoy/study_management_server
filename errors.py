class APIError(Exception):
    def getStatusCode(self):
        return 500

class UnauthorizedError(APIError):
    def getStatusCode(self):
        return 401

class ForbiddenError(APIError):
    def getStatusCode(self):
        return 403
