import requests
import json

base_url = "http://127.0.0.1:5000/"
class APITester():
    def __init__(self):
        self.requestType = "GET"
        self.url = "studies"
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.data = {}
    def sendRequest(self):
        url = base_url + self.url
        if self.requestType=="GET":
            return requests.get(url)
        if self.requestType=="POST":
            return requests.post(url, data=json.dumps(self.data), headers=self.headers)
        if self.requestType=="PUT":
            return requests.put(url, data=json.dumps(self.data), headers=self.headers)
        if self.requestType=="DELETE":
            return requests.delete(url)
