#Korona bot for Discord

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

import discord
import json
import requests
from discord.ext import commands

myToken = 'Njg5MTE0MzgxODUzNzg2MzE4.Xm_1DA.4LegCpYqRrT0BKhIf9D5g0IgMAQ'

#use '.' before command
client = commands.Bot(command_prefix = '.')
response = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')

#just test that bot easy ready to use
@client.event
async def on_ready():
    print('Bot is ready.')

#posts Pirkanmaa 
@client.command()
async def koronaP(ctx):
    P = getPirkanmaaKorona()
    for i in P:
        await ctx.send(i)

#posts Finland
@client.command()
async def korona(ctx):
    P = getFinlandKorona()
    for i in P:
        await ctx.send(i)

#if someone mentions corona posts corona bottle
@client.event
async def on_message(message):
    if "corona" in message.content.lower():
        channel = message.channel
        await channel.send(file=discord.File('corona.jpeg'))
    
    #you need this that commands wont't break
    await client.process_commands(message)

def getFinlandKorona():
    P = []
    P.append(getFinlandConfirmed(response))
    P.append(getFinlandDeaths(response))
    P.append(getFinlandRecovered(response))
    return P

def getPirkanmaaKorona():
    P = []
    P.append(getPirkanmaaConfirmed(response))
    P.append(getPirkanmaaDeaths(response))
    P.append(getPirkanmaaRecovered(response))
    return P
    
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def getFinlandConfirmed(obj):
    print('{}: {}'.format("Confirmed", len(obj.json()['confirmed'])))
    return "{}: {}".format("Finland confirmed", len(obj.json()['confirmed']))

def getFinlandDeaths(obj):
    print("{}: {}".format("Deaths", len(obj.json()['deaths'])))
    return "{}: {}".format("Finland deaths", len(obj.json()['deaths']))

def getFinlandRecovered(obj):
    print("{}: {}".format("Recovered", len(obj.json()['recovered'])))
    return "{}: {}".format("Finland recovered", len(obj.json()['recovered']))

def getPirkanmaaConfirmed(obj):
    pConf = 0
    for i in obj.json()['confirmed']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa confirmed", pConf))
    return "{}: {}".format("Pirkanmaa confirmed", pConf)

def getPirkanmaaRecovered(obj):
    pConf = 0
    for i in obj.json()['recovered']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa confirmed", pConf))
    return "{}: {}".format("Pirkanmaa confirmed", pConf)

def getPirkanmaaDeaths(obj):
    pConf = 0
    for i in obj.json()['deaths']:
        if i['healthCareDistrict'] == 'Pirkanmaa':
            pConf += 1
    print("{}: {}".format("Pirkanmaa deaths", pConf))
    return "{}: {}".format("Pirkanmaa deaths", pConf)

#here you enter your bot token
client.run(myToken)
