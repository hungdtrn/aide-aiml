import os
import requests
import json
from client import welcome, set_url, dailySummary, dailyIndicator, chatStream



def unit_tests():
    # Test local server
    print("Testing local server")
    set_url("http://127.0.0.1:8080")
    print("Welcome test")
    print(welcome( obj = {"userId": 0}))
    print("Daily summary test")
    print(dailySummary(obj =  {"userId": 0, "n" : 1}))
    print("Daily indicator test")
    print(dailyIndicator(obj = {"userId": 0, "n" : 5}))
    print("Chat stream test")
    print(chatStream({'userId': 0, 'message': "how are you today"}))

    # Test gcp server
    print("Testing GCP server")
    set_url("https://aide-server-ogdrzymura-km.a.run.app")
    print("Welcome test")
    print(welcome( obj = {"userId": 0}))
    print("Daily summary test")
    print(dailySummary(obj =  {"userId": 0, "n" : 1}))
    print("Daily indicator test")
    print(dailyIndicator(obj = {"userId": 0, "n" : 5}))
    print("Chat stream test")
    print(chatStream({'userId': 0, 'message': "how are you today"}))

    pass



if __name__ == "__main__":
    unit_tests()
