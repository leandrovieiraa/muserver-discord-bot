# bot.py
import os
import random
import pyodbc
from discord.ext import commands
from dotenv import load_dotenv

# Discord Token
TOKEN = 'YOUR_DISCORD_APP_TOKEN'

# Server configurations
DB_HOST = 'xxxx'
DB_PORT = 'xxxx'
DB_USER = 'xxxx'
DB_PASS = 'xxxx'
DB_NAME = 'MuOnline'

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DB_HOST+','+DB_PORT+';DATABASE='+DB_NAME+';UID='+DB_USER+';PWD='+ DB_PASS)
cursor = cnxn.cursor()

load_dotenv()
bot = commands.Bot(command_prefix='!')

def getTop50Resets(cursor=''):
    top50 = []
    query = 'SELECT TOP 50 Name, cLevel, Resets FROM Character WHERE CtlCode = 0 ORDER BY Resets, cLevel DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    current_position = 1
    for row in rows:
        character = dict()
        character['name'] = row[0]
        character['level'] = row[1]
        character['resets'] = row[2]
        character['position'] = current_position
        top50.append(character)
        current_position += 1
    return top50

def getTop50Pks(cursor):
    top50 = []
    query ='SELECT TOP 50 Name, PkCount, PkLevel, PkTime FROM Character WHERE CtlCode = 0 AND PkCount != 0 ORDER BY PkLevel, PkCount DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    current_position = 1
    for row in rows:
        character = dict()
        character['name'] = row[0]
        character['pkcount'] = row[1]
        character['pklevel'] = row[2]
        character['pktime'] = row[3]
        character['position'] = current_position
        top50.append(character)
        current_position += 1
    return top50

@bot.command(name='ranking')
async def top50_resets(ctx):
    top50 = getTop50Resets(cursor)
    message = ''
    for character in top50:
        message += f"#{character['position']} Name: {character['name']} - Level: {character['level']} - Resets: {character['resets']}\n"
    await ctx.send(message)

@bot.command(name='pk')
async def top50_resets(ctx):
    top50 = getTop50Pks(cursor)
    message = ''
    for character in top50:
        message += f"#{character['position']} Name: {character['name']} - Pk Count: {character['pkcount']} - Pk Level: {character['pklevel']} - Pk Time: {character['pktime']}\n"
    await ctx.send(message)

bot.run(TOKEN)