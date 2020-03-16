#Test file for api calls

"""
Datasource:
MIT License

Copyright (c) 2020 Helsingin Sanomat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import json
import requests

response = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def getFinlandConfirmed(obj):
    print('{}: {}'.format("Confirmed", len(obj.json()['confirmed'])))

def getFinlandDeaths(obj):
    print("{}: {}".format("Deaths", len(obj.json()['deaths'])))

def getFinlandRecovered(obj):
    print("{}: {}".format("Recovered", len(obj.json()['recovered'])))

def getPirkanmaaConfirmed(obj):
    pConf = 0
    for i in obj.json()['confirmed']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa confirmed", pConf))

def getPirkanmaaRecovered(obj):
    pConf = 0
    for i in obj.json()['recovered']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa recovered", pConf))

def getPirkanmaaDeaths(obj):
    pConf = 0
    for i in obj.json()['deaths']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa deaths", pConf))



jprint(response.json()['confirmed'])

getFinlandConfirmed(response)
getFinlandDeaths(response)
getFinlandRecovered(response)

print()
getPirkanmaaConfirmed(response)
getPirkanmaaRecovered(response)
getPirkanmaaDeaths(response)
