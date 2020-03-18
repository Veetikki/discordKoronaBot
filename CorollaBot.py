"""
Korona bot for Discord
Datasource:
Finland specific (c) 2020 Helsingin Sanomat https://github.com/HS-Datadesk/koronavirus-avoindata
Global data copyright 2020 Johns Hopkins University https://github.com/CSSEGISandData/COVID-19
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

myToken = 'your token'

#use '.' before command
client = commands.Bot(command_prefix = '.')
response = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')
globalDataUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv'

#Ei sisällä HUS koska poikkeus APIssa
sairaanhoitopiirit = [
                    ["EK", "Etelä-Karjala"],
                    ["EP", "Etelä-Pohjanmaa"],
                    ["ES", "Etelä-Savo"],
                    ["IS", "Itä-Savo"],
                    ["KAI", "Kainuu"],
                    ["KH", "Kanta-Häme"],
                    ["KP", "Keski-Pohjanmaa"],
                    ["KS", "Keski-Suomi"],
                    ["KYM", "Kymenlaakso"],
                    ["L", "Lappi"],
                    ["LP", "Länsi-Pohja"],
                    ["P", "Pirkanmaa"],
                    ["PK", "Pohjois-Karjala"],
                    ["PP", "Pohjois-Pohjanmaa"],
                    ["PS", "Pohjois-Savo"],
                    ["PH", "Päijät-Häme"],
                    ["S", "Satakunta"],
                    ["V", "Vaasa"],
                    ["VS", "Varsinais-Suomi"]
                    ]

def getResponse():
    res = requests.get('https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData')
    return res

#Connects to globaldata
def conncetToGlobal():
    d = datetime.today().strftime('%m-%d-%Y')
    res = globalDataUrl.replace('{date}', d)

    for i in range(1,10):
        try:
            df = pd.read_csv(res, error_bad_lines=False)
        except:
            try:
                d = date.today() - timedelta(days=i)
                strD = d.strftime('%m-%d-%Y')
                
                res = globalDataUrl.replace('{date}', strD)
                df = pd.read_csv(res, error_bad_lines=False)
                return [df, d]
            except:
                if i == 10:
                    print("Couldn't connect API")
                    raise Exception("Couldn't connect API")

#just test that bot ready to use
@client.event
async def on_ready():
    print('Bot is ready.')

#Checks arguments
@client.command(brief='COVID-19 situations. See avaible arguments with help.', description='Avaible arguments:\n-global\n-Country name\n-sairaanhoitopiirien lyhenteet ks. https://www.kuntaliitto.fi/sosiaali-ja-terveysasiat/sairaanhoitopiirien-jasenkunnat\nExamples: .korona Finland and .korona P\nAll not working at this moment.')
async def korona(ctx, arg):
    try:
        countries = conncetToGlobal()[0]['Country/Region']
        #muutetaan stringiksi
        strCountries = [str(i) for i in countries]

        #Suomi erikseen, koska käyttää parempaa HS:n APIA
        if arg == 'Finland':
            P = getFinlandKorona()
            await ctx.send('{}{}: {}{}{}: {}{}{}: {}'.format("Current Finland situation:\n", "Confirmed", P[0], "\n", "Deaths", P[1], "\n", "Recovered", P[2]))
        elif arg in strCountries and arg != 'Finland':
            P = getCountryKorona(arg)
            await ctx.send('{}{}: {}{}{}: {}{}{}: {}{}{}'.format(arg + " situation:\n", "Confirmed", P[0], "\n", "Deaths", P[1], "\n", "Recovered", P[2], "\nLast data from ", P[3]))
        elif arg == 'global':
            P = getGlobalKorona()
            await ctx.send('{}{}: {}{}{}: {}{}{}: {}{}{}'.format("Global situation:\n", "Confirmed", P[0], "\n", "Deaths", P[1], "\n", "Recovered", P[2], "\nLast data from ", P[3]))
        elif len(arg) <= 3:
            #HUSille on APIssa poikkeus
            if arg == "HUS":
                P = getSPKorona(arg)
                await ctx.send('{}{}: {}{}{}: {}{}{}: {}'.format("Current Helsingin ja Uudenmaan sairaanhoitopiiri situation:\n", "Confirmed", P[0], "\n", "Deaths", P[1], "\n", "Recovered", P[2]))
            else:
                for i in sairaanhoitopiirit:
                    if arg in i:
                        P = getSPKorona(i[1])
                        await ctx.send('{}{}: {}{}{}: {}{}{}: {}'.format("Current " + i[1] + " situation:\n", "Confirmed", P[0], "\n", "Deaths", P[1], "\n", "Recovered", P[2]))
                        break
        else:
            await ctx.send("En tiedä. Lisätään myöhemmin.")
    except:
        await ctx.send("Couldn't connect API")

#sends private message of avaible countries
@client.command(brief='Lists avaible countries')
async def listCountries(ctx):
    countries = conncetToGlobal()[0]['Country/Region']
    #muutetaan stringiksi
    strCountries = [str(i) for i in countries]
    strCountries.sort()

    message = strCountries[0]
    doubleCheck = [message]

    for i in strCountries:
        if i not in doubleCheck:
            s = "\n" + i
            message += s
            doubleCheck.append(i)
    
    user = ctx.message.author
    await user.send(message)


#if someone mentions corona posts corona bottle
@client.event
async def on_message(message):
    #if you wan to use picture instead you use:
    #file=discord.File('corona.jpeg')
    channel = message.channel
    if message.author.bot: return
    elif "corona" in message.content.lower():
        await channel.send("<:corolla:689538487430414464>")
    elif "korona" in message.content.lower() and ".korona" not in message.content.lower() and ".help" not in message.content.lower():
        await channel.send('Ai tarkoititko...')
        await channel.send("<:corolla:689538487430414464>")
    elif message.content.startswith('haloo?'):
        await channel.send('haloo')
    #you need this that commands wont't break
    await client.process_commands(message)

def getFinlandKorona():
    res = response
    #if API is updating or down
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
    res = conncetToGlobal()
    df = res[0]
    d = res[1]

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
    
    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]


def getCountryKorona(country):
    res = conncetToGlobal()
    df = res[0]
    d = res[1]

    confirmed = 0
    deaths = 0
    recovered = 0

    #if row match with country
    for i in range(len(df['Country/Region'])):
        if str(df['Country/Region'][i]) == country:
            confirmed += df['Confirmed'][i]
            deaths += df['Deaths'][i]
            recovered += df['Recovered'][i]

    print(confirmed)
    print(deaths)
    print(recovered)
    
    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]

#argumenttina sairaanhoitopiiri
def getSPKorona(sp):
    res = response

    #if API is updating or down
    try:
        res = getResponse()
    except:
        print("Couldn't get response from api")
    P = []
    P.append(getSPConfirmed(res, sp))
    P.append(getSPDeaths(res, sp))
    P.append(getSPRecovered(res, sp))
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

def getSPConfirmed(obj, sp):
    pConf = 0
    for i in obj.json()['confirmed']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    print("{}: {}".format(sp + " confirmed", pConf))
    return "{}: {}".format(sp + " confirmed", pConf)

def getSPRecovered(obj, sp):
    pConf = 0
    for i in obj.json()['recovered']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    print("{}: {}".format(sp + " confirmed", pConf))
    return "{}: {}".format(sp + " confirmed", pConf)

def getSPDeaths(obj, sp):
    pConf = 0
    for i in obj.json()['deaths']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    print("{}: {}".format(sp + " deaths", pConf))
    return "{}: {}".format(sp + " deaths", pConf)

#here you enter your bot token
client.run(myToken)
