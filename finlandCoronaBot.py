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
import re
import json
import csv
import requests
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from discord.ext import commands

myToken = 'Njg5MTE0MzgxODUzNzg2MzE4.Xm_1DA.4LegCpYqRrT0BKhIf9D5g0IgMAQ'

#use '.' before command
client = commands.Bot(command_prefix = '.')
response = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')
globalDataUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv'

def getResponse():
    res = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')
    return res

#just test that bot easy ready to use
@client.event
async def on_ready():
    print('Bot is ready.')

#posts Pirkanmaa 
@client.command(brief='Pirkanmaa COVID-19 situation')
async def koronaP(ctx):
    P = getPirkanmaaKorona()
    for i in P:
        await ctx.send(i)

#posts Finland
@client.command(brief='Finland COVID-19 situation')
async def korona(ctx):
    P = getFinlandKorona()
    for i in P:
        await ctx.send(i)

#posts Finland
@client.command(brief='Global COVID-19 situation')
async def koronaG(ctx):
    P = getGlobalKorona()
    await ctx.send("Global situation:")
    await ctx.send('{}: {}'.format("Confirmed", P[0]))
    await ctx.send('{}: {}'.format("Deaths", P[1]))
    await ctx.send('{}: {}'.format("Recovered", P[2]))

#posts Sannawave
@client.command(brief='Good song')
async def marin(ctx):
    await ctx.send("https://soundcloud.com/user-11140692/sannawave-1")

#file=discord.File('corona.jpeg')
#if someone mentions corona posts corona bottle
@client.event
async def on_message(message):
    channel = message.channel
    if message.author.bot: return
    elif "corona" in message.content.lower():
        await channel.send("<:corolla:689538487430414464>")
    elif "korona" in message.content.lower() and ".korona" not in message.content.lower():
        await channel.send('Ai tarkoititko...')
        await channel.send("<:corolla:689538487430414464>")
    elif "peruttu?" in message.content.lower():
        await channel.send("""```PJ-päivä peruttu
Vicon jeccusitsit peruttu
Aurajokilaivuritutkinto peruttu
Pelkkää kotona oloa annettu
Tek-akatemia siirretty
Jyväsmetro siirretty
SSL:n statistikaan kevätseminaari peruttu
Pelkkää kotona oloa annettu
kopokonferenssi peruttu
titen vujut peruttu
indecsin vujut peruttu
Pelkkää kotona oloa annettu
                            ```""")
    elif message.content.startswith('haloo?'):
        await channel.send('haloo')
    #elif re.findall('pr[ö|u]+t', message.content.lower()) != []:
        #await channel.send('prööt prööt ja korona levis taas')
    #Ei voi laittaa laulua, koska liian pitkä
    elif "makedonia?" in message.content.lower():
        await channel.send("Kysy Karilta")
    elif "mpoke?" in message.content.lower():
        await channel.send("https://www.youtube.com/watch?v=3lj4jEZHYYg")
    #you need this that commands wont't break
    await client.process_commands(message)

def getFinlandKorona():
    res = response
    try:
        res = getResponse()
    except:
        print("Couldn't get response from api")
    P = []
    P.append(getFinlandConfirmed(res))
    P.append(getFinlandDeaths(res))
    P.append(getFinlandRecovered(res))
    return P

def getGlobalKorona():
    d = datetime.today().strftime('%m-%d-%Y')
    res = globalDataUrl.replace('{date}', d)

    #Tries to get data from last 5 days
    for i in range(1,5):
        try:
            df = pd.read_csv(res, error_bad_lines=False)
        except:
            print("{} {}".format("Couldn't get ", d))
            try:
                d = date.today() - timedelta(days=i)
                d = d.strftime('%m-%d-%Y')
                
                res = globalDataUrl.replace('{date}', d)
                df = pd.read_csv(res, error_bad_lines=False)
                break
            except:
                print("{} {}".format("Couldn't get ", d))
    #print(res)
    
    #print(df['Confirmed'])

    #Lets calculate confirmed, deaths and recovered
    confirmed = 0
    for i in df['Confirmed']:
        confirmed += i

    deaths = 0
    for i in df['Deaths']:
        deaths += i

    recovered = 0
    for i in df['Recovered']:
        recovered += i

    print(confirmed)
    print(deaths)
    print(recovered)
    
    return [confirmed, deaths, recovered]

def getPirkanmaaKorona():
    res = response
    try:
        res = getResponse()
    except:
        print("Couldn't get response from api")
    P = []
    P.append(getPirkanmaaConfirmed(res))
    P.append(getPirkanmaaDeaths(res))
    P.append(getPirkanmaaRecovered(res))
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
