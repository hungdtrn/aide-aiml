import requests
import json
from client import welcome, set_url, dailySummary



def unit_tests():
    # Test local server
    print("Testing local server")
    set_url("http://127.0.0.1:8080")
    # print(welcome( obj = {"userId": 0})) # Welcome test
    print(dailySummary(obj =  {"userId": 0, "n" : 1}))

    # #Test gcp server
    print("Testing GCP server")
    # set_url("https://aide-server-ogdrzymura-km.a.run.app")
    # print(welcome( obj = {"userId": 0})) # Welcome test
    # print(dailySummary(obj =  {"userId": 0, "n" : 1}))



    pass



if __name__ == "__main__":
    unit_tests()
