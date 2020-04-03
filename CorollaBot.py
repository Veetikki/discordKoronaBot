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

myToken = 'your token'

#use '.' before command
client = commands.Bot(command_prefix = '.')
HSurl = 'https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData/v2'
globalConfUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
globalDeathsUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
globalRecUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

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
            #jos käyttää linuxia, niin käytä d.strftime('%-m/%d/%y')
            strD = d.strftime('%#m/%#d/%y')
            #katotaan onko dataa
            conf[strD]

            return [conf, deaths, rec, d]
        except:
            if i == 10:
                print("Couldn't connect API")
                raise Exception("Couldn't connect API")

#Get countries
strCountries = [str(i) for i in connectToGlobal()[0]['Country/Region']]

#just test that bot ready to use
@client.event
async def on_ready():
    print('Bot is ready.')

#Checks arguments
@client.command(brief='COVID-19 situations. See avaible arguments with help.', description='Avaible arguments:\n-global\n-Country name\n-sairaanhoitopiirien lyhenteet ks. https://www.kuntaliitto.fi/sosiaali-ja-terveysasiat/sairaanhoitopiirien-jasenkunnat\nExamples: .korona Finland and .korona P\nAll not working at this moment.')
async def korona(ctx, arg):
    try:
        #Suomi erikseen, koska käyttää parempaa HS:n APIA
        if arg == 'Finland':
            P = getFinlandKorona()
            await ctx.send('{}{}: {:,} (+{:,})\n{}: {:,} (+{:,})\n{}: {:,} (+{:,})'.format("Current Finland situation:\n", "Confirmed", P[0][0], P[0][1], "Deaths", P[1][0], P[1][1], "Recovered", P[2][0], P[2][1]))
        elif arg in strCountries and arg != 'Finland':
            P = getCountryKorona(arg)
            await ctx.send('{}{}: {:,} (+{:,})\n{}: {:,} (+{:,})\n{}: {:,} (+{:,}){}{}'.format(arg + " situation:\n", "Confirmed", P[0][0], P[0][1], "Deaths", P[1][0], P[1][1], "Recovered", P[2][0],P[2][1], "\nLast data from ", P[3]))
        elif arg == 'global':
            P = getGlobalKorona()
            await ctx.send('{}{}: {:,} (+{:,})\n{}: {:,} (+{:,})\n{}: {:,} (+{:,}){}{}'.format("Global situation:\n", "Confirmed", P[0][0], P[0][1], "Deaths", P[1][0], P[1][1], "Recovered", P[2][0],P[2][1], "\nLast data from ", P[3]))
        elif len(arg) <= 3:
            #HUSille on APIssa poikkeus
            if arg == "HUS":
                P = getSPKorona(arg)
                await ctx.send('{}{}: {:,} (+{:,})\n{}: {:,} (+{:,})\n{}: {:,} (+{:,})'.format("HUS situation:\n", "Confirmed", P[0][0], P[0][1], "Deaths", P[1][0], P[1][1], "Recovered", P[2][0], P[2][1]))
            else:
                for i in sairaanhoitopiirit:
                    if arg in i:
                        P = getSPKorona(i[1])
                        await ctx.send('{}{}: {:,} (+{:,})\n{}: {:,} (+{:,})\n{}: {:,} (+{:,})'.format(i[1] + " situation:\n", "Confirmed", P[0][0], P[0][1], "Deaths", P[1][0], P[1][1], "Recovered", P[2][0], P[2][1]))
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
        P = [getFinlandConfirmed(res), getFinlandDeaths(res), getFinlandRecovered(res)]
        return P
    except:
        print("Couldn't get response from api")

def getGlobalKorona():
    res = connectToGlobal()
    conf = res[0]
    dea = res[1]
    rec = res[2]
    d = res[3]
    yd = d - timedelta(days=1)
    #huono muotoilu tässäkin
    strD = d.strftime('%#m/%#d/%y')
    strYd = yd.strftime('%#m/%#d/%y')

    #Lets calculate confirmed, deaths and recovered
    #käyttää jostain syystä floattia joka paikassa
    confirmed = [sum(conf[strD]), sum(conf[strD]) - sum(conf[strYd])]
    deaths = [sum(dea[strD]), sum(dea[strD]) - sum(dea[strYd])]
    recovered = [sum(rec[strD]), sum(rec[strD]) - sum(rec[strYd])]

    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]


def getCountryKorona(country):
    res = connectToGlobal()
    conf = res[0]
    dea = res[1]
    rec = res[2]
    d = res[3]
    yd = d - timedelta(days=1)
    #huono muotoilu tässäkin
    strD = d.strftime('%#m/%#d/%y')
    strYd = yd.strftime('%#m/%#d/%y')

    #Lets calculate confirmed, deaths and recovered
    #todays and yesterday
    tConf = [conf[strD][i] for i in range(len(conf['Country/Region'])) if str(conf['Country/Region'][i]) == country]
    yConf = [conf[strYd][i] for i in range(len(conf['Country/Region'])) if str(conf['Country/Region'][i]) == country]
    confirmed = [sum(tConf), sum(tConf) - sum(yConf)]

    tDea = [dea[strD][i] for i in range(len(dea['Country/Region'])) if str(dea['Country/Region'][i]) == country]
    yDea = [dea[strYd][i] for i in range(len(dea['Country/Region'])) if str(dea['Country/Region'][i]) == country]
    deaths = [sum(tDea), sum(tDea) - sum(yDea)]

    tRec = [rec[strD][i] for i in range(len(rec['Country/Region'])) if str(rec['Country/Region'][i]) == country]
    yRec = [rec[strYd][i] for i in range(len(rec['Country/Region'])) if str(rec['Country/Region'][i]) == country]
    recovered = [sum(tRec), sum(tRec) - sum(yRec)]
    
    return [confirmed, deaths, recovered, d.strftime('%d-%m-%Y')]

#argumenttina sairaanhoitopiiri
def getSPKorona(sp):
    #if API is updating or down
    try:
        res = getResponse()
        P = [getSPConfirmed(res, sp), getSPDeaths(res, sp), getSPRecovered(res, sp)]
        return P
    except:
        print("Couldn't get response from api")
    
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def getFinlandConfirmed(obj):
    print('{}: {} {}'.format("Confirmed", len(obj.json()['confirmed']), sum([1 for i in obj.json()['confirmed'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])))
    return [len(obj.json()['confirmed']), len(obj.json()['confirmed']) - sum([1 for i in obj.json()['confirmed'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])]

def getFinlandDeaths(obj):
    print('{}: {} {}'.format("Deaths", len(obj.json()['deaths']), sum([1 for i in obj.json()['deaths'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])))
    return [len(obj.json()['deaths']), len(obj.json()['deaths']) - sum([1 for i in obj.json()['deaths'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])]

def getFinlandRecovered(obj):
    print('{}: {} {}'.format("Recovered", len(obj.json()['recovered']), sum([1 for i in obj.json()['recovered'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])))
    return [len(obj.json()['recovered']), len(obj.json()['recovered']) - sum([1 for i in obj.json()['recovered'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat()])]

def getSPConfirmed(obj, sp):
    conf = sum([1 for i in obj.json()['confirmed'] if i['healthCareDistrict'] == sp])
    return [conf, conf - sum([1 for i in obj.json()['confirmed'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat() and i['healthCareDistrict'] == sp])]

def getSPRecovered(obj, sp):
    rec = sum([1 for i in obj.json()['recovered'] if i['healthCareDistrict'] == sp])
    return [rec, rec - sum([1 for i in obj.json()['recovered'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat() and i['healthCareDistrict'] == sp])]

def getSPDeaths(obj, sp):
    deaths = sum([1 for i in obj.json()['deaths'] if i['healthCareDistrict'] == sp])
    return [deaths, deaths - sum([1 for i in obj.json()['deaths'] if i['date'] < (datetime.today() - timedelta(days=1)).isoformat() and i['healthCareDistrict'] == sp])]

#here you enter your bot token
client.run(myToken)
