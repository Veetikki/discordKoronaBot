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
import math
from datetime import datetime, timedelta, date
from discord.ext import commands

myToken = 'Njg5MTE0MzgxODUzNzg2MzE4.XnI4UQ.IbLzg765_F-zdWpMUrdcAfJo-VQ'

#use '.' before command
client = commands.Bot(command_prefix = '.')
HSurl = 'https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData'
globalConfUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
globalDeathsUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv'
globalRecUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'

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
    res = requests.get(HSurl)
    return res

#Connects to globaldata
def connectToGlobal():
    conf = pd.read_csv(globalConfUrl, error_bad_lines=False)
    deaths = pd.read_csv(globalDeathsUrl, error_bad_lines=False)
    rec = pd.read_csv(globalRecUrl, error_bad_lines=False)

    for i in range(0,10):
        try:
            d = date.today() - timedelta(days=i)
            strD = d.strftime('%#m/%d/%y')
            #katotaan onko dataa
            conf[strD]

            return [conf, deaths, rec, d]
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
        #haetaan maat aina kun hakee. Ei kauhean optimaalista, mutta päivitellään myöhemmin.
        countries = connectToGlobal()[0]['Country/Region']
        #muutetaan stringiksi
        strCountries = [str(i) for i in countries]

        #Suomi erikseen, koska käyttää parempaa HS:n APIA
        if arg == 'Finland':
            P = getFinlandKorona()
            await ctx.send('{}{}: {:,}\n{}: {:,}\n{}: {:,}'.format("Current Finland situation:\n", "Confirmed", P[0], "Deaths", P[1], "Recovered", P[2]))
        elif arg in strCountries and arg != 'Finland':
            P = getCountryKorona(arg)
            await ctx.send('{}{}: {:,}\n{}: {:,}\n{}: {:,}{}{}'.format(arg + " situation:\n", "Confirmed", P[0], "Deaths", P[1], "Recovered", P[2], "\nLast data from ", P[3]))
        elif arg == 'global':
            P = getGlobalKorona()
            await ctx.send('{}{}: {:,}\n{}: {:,}\n{}: {:,}{}{}'.format("Global situation:\n", "Confirmed", P[0], "Deaths", P[1], "Recovered", P[2], "\nLast data from ", P[3]))
        elif len(arg) <= 3:
            #HUSille on APIssa poikkeus
            if arg == "HUS":
                P = getSPKorona(arg)
                await ctx.send('{}{}: {:,}\n{}: {:,}\n{}: {:,}'.format("Current Helsingin ja Uudenmaan sairaanhoitopiiri situation:\n", "Confirmed", P[0], "Deaths", P[1], "Recovered", P[2]))
            else:
                for i in sairaanhoitopiirit:
                    if arg in i:
                        P = getSPKorona(i[1])
                        await ctx.send('{}{}: {:,}\n{}: {:,}\n{}: {:,}'.format("Current " + i[1] + " situation:\n", "Confirmed", P[0], "Deaths", P[1], "Recovered", P[2]))
                        break
        else:
            await ctx.send("En tiedä.")
    except:
        await ctx.send("Couldn't connect API")

#sends private message of avaible countries
@client.command(brief='Lists avaible countries')
async def listCountries(ctx):
    countries = connectToGlobal()[0]['Country/Region']
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
    #if API is updating or down
    try:
        res = getResponse()
        P = []
        P.append(getFinlandConfirmed(res))
        P.append(getFinlandDeaths(res))
        P.append(getFinlandRecovered(res))
        return P
    except:
        print("Couldn't get response from api")

def getGlobalKorona():
    res = connectToGlobal()
    conf = res[0]
    dea = res[1]
    rec = res[2]
    d = res[3]
    #huono muotoilu tässäkin
    strD = d.strftime('%#m/%d/%y')

    #Lets calculate confirmed, deaths and recovered
    #käyttää jostain syystä floattia joka paikassa
    confirmed = 0
    for i in conf[strD]:
        if not math.isnan(i):
            confirmed += i

    deaths = 0
    for i in dea[strD]:
        if not math.isnan(i):
            deaths += i

    recovered = 0
    for i in rec[strD]:
        if not math.isnan(i):
            recovered += i

    #muutetaan kokonaisluvuksi, koska jostain kumman syystä käyttää floattia
    confirmed = int(round(confirmed))
    deaths = int(round(deaths))
    recovered = int(round(recovered))

    print(confirmed)
    print(deaths)
    print(recovered)
    
    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]


def getCountryKorona(country):
    res = connectToGlobal()
    conf = res[0]
    dea = res[1]
    rec = res[2]
    d = res[3]
    strD = d.strftime('%#m/%d/%y')

    #Lets calculate confirmed, deaths and recovered
    confirmed = 0
    for i in range(len(conf['Country/Region'])):
        if str(conf['Country/Region'][i]) == country and not math.isnan(conf[strD][i]):
            confirmed += conf[strD][i]

    deaths = 0
    for i in range(len(dea['Country/Region'])):
        if str(dea['Country/Region'][i]) == country and not math.isnan(dea[strD][i]):
            deaths += dea[strD][i]

    recovered = 0
    for i in range(len(rec['Country/Region'])):
        if str(rec['Country/Region'][i]) == country and not math.isnan(rec[strD][i]):
            recovered += rec[strD][i]

    confirmed = int(round(confirmed))
    deaths = int(round(deaths))
    recovered = int(round(recovered))

    print(confirmed)
    print(deaths)
    print(recovered)
    
    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]

#argumenttina sairaanhoitopiiri
def getSPKorona(sp):
    #if API is updating or down
    try:
        res = getResponse()
        P = []
        P.append(getSPConfirmed(res, sp))
        P.append(getSPDeaths(res, sp))
        P.append(getSPRecovered(res, sp))
        return P
    except:
        print("Couldn't get response from api")
    
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def getFinlandConfirmed(obj):
    print('{}: {}'.format("Confirmed", len(obj.json()['confirmed'])))
    return len(obj.json()['confirmed'])

def getFinlandDeaths(obj):
    print("{}: {}".format("Deaths", len(obj.json()['deaths'])))
    return len(obj.json()['deaths'])

def getFinlandRecovered(obj):
    print("{}: {}".format("Recovered", len(obj.json()['recovered'])))
    return len(obj.json()['recovered'])

def getSPConfirmed(obj, sp):
    pConf = 0
    for i in obj.json()['confirmed']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    return pConf

def getSPRecovered(obj, sp):
    pConf = 0
    for i in obj.json()['recovered']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    return pConf

def getSPDeaths(obj, sp):
    pConf = 0
    for i in obj.json()['deaths']:
        if i['healthCareDistrict'] == sp:
            pConf += 1
    return pConf

#here you enter your bot token
client.run(myToken)
