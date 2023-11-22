import requests
import json
from client import welcome, set_url



def unit_tests():
    # Test local server
    set_url("http://127.0.0.1:8080")
    print(welcome( obj = {"userId": 0}))

    # Test gcp server
    # set_url("https://aide-server-ogdrzymura-km.a.run.app")
    # print(welcome( obj = {"userId": 0}))

    pass



if __name__ == "__main__":
    unit_tests()
