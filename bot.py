# bot.py
import os
import random
import pyodbc
import discord
from datetime import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv
from threading import Timer

# Discord Token
TOKEN = ''

# Server configurations
DB_HOST = ''
DB_PORT = ''
DB_USER = ''
DB_PASS = ''
DB_NAME = ''

# ANTICHEAT
TIME_SEARCH_HACKER = 30 # minutes
ANTICHEAT_CHANNEL = None

# Auto reset and misc
SYSTEM_CHANNEL = None
TIME_RESET = 2

# Create connection with SQL Server
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DB_HOST+','+DB_PORT+';DATABASE='+DB_NAME+';UID='+DB_USER+';PWD='+ DB_PASS)
cursor = cnxn.cursor()

# Create Discord
load_dotenv()
bot = commands.Bot(command_prefix='!')
client = discord.Client()

def findCharacterClass(classId):
    cClass = None
    if classId == 0:
        cClass = "Dark Wizard"
    elif classId == 1:
        cClass = "Soul Master"
    elif classId == 16:
        cClass = "Dark Knight"
    elif classId == 17:
        cClass = "Blade Knight"
    elif classId == 32:
        cClass = "Fairy Elf"
    elif classId == 33:
        cClass = "Muse Elf"
    elif classId == 48:
        cClass = "Magic Gladiator"
    elif classId == 64:
        cClass = "Dark Lord"
    return cClass

def getTop50Resets(cursor=''):
    top50 = []
    query = 'SELECT TOP 25 Name, cLevel, Resets, Class FROM Character WHERE CtlCode = 0 ORDER BY Resets DESC, cLevel DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    current_position = 1
    for row in rows:
        character = dict()
        character['name'] = row[0]
        character['level'] = row[1]
        character['resets'] = row[2]
        character['position'] = current_position
        character['class'] = findCharacterClass(int(row[3]))
        top50.append(character)
        current_position += 1
    return top50

def getTop50Pks(cursor):
    top50 = []
    query ='SELECT TOP 25 Name, PkCount, PkLevel, PkTime, Class FROM Character WHERE CtlCode = 0 AND PkCount != 0 ORDER BY PkLevel DESC, PkCount DESC'
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
        character['class'] = findCharacterClass(int(row[4]))
        top50.append(character)
        current_position += 1
    return top50

def findPossibleWarehouseHackers(cursor):
    warehouse_hackers = []
    query ='''
        select * from warehouse where
        ((charindex (0xbf, items) %10=8)
        or (charindex (0xff, items) %10=8)
        or (charindex (0x7f, items) %10=8)
        or (charindex (0x37, items) %10=8)
        or (charindex (0x2f, items) %10=8)
        or (charindex (0x2e, items) %10=8)
        or (charindex (0x1f, items) %10=8)
        or (charindex (0x3b, items) %10=8)
        or (charindex (0x39, items) %10=8)
        or (charindex (0x3d, items) %10=8)
        or (charindex (0x3e, items) %10=8)
        or (charindex (0x36, items) %10=8)
        or (charindex (0x3a, items) %10=8)
        or (charindex (0x0f, items) %10=8)
        or (charindex (0x17, items) %10=8)
        or (charindex (0x27, items) %10=8)
        or (charindex (0x3f, items) %10=8))
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        account = dict()
        account['account_id'] = row[0]
        warehouse_hackers.append(account)
    return warehouse_hackers

def findPossibleInventoryHackers(cursor):
    inventory_hackers = []
    query ='''
        select * from character where ((charindex (0xbf, inventory) %10=8)
        or (charindex (0xff, inventory) %10=8)
        or (charindex (0x7f, inventory) %10=8)
        or (charindex (0x37, inventory) %10=8)
        or (charindex (0x2f, inventory) %10=8)
        or (charindex (0x2e, inventory) %10=8)
        or (charindex (0x1f, inventory) %10=8)
        or (charindex (0x3b, inventory) %10=8)
        or (charindex (0x39, inventory) %10=8)
        or (charindex (0x3d, inventory) %10=8)
        or (charindex (0x3e, inventory) %10=8)
        or (charindex (0x36, inventory) %10=8)
        or (charindex (0x3a, inventory) %10=8)
        or (charindex (0x0f, inventory) %10=8)
        or (charindex (0x17, inventory) %10=8)
        or (charindex (0x27, inventory) %10=8)
        or (charindex (0x3f, inventory) %10=8))
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        account = dict()
        account['account_id'] = row[0]
        inventory_hackers.append(account)
    return inventory_hackers

def autoReset():
    dt = datetime.now().isoformat()
    try:
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DB_HOST+','+DB_PORT+';DATABASE='+DB_NAME+';UID='+DB_USER+';PWD='+ DB_PASS)
        cursor = cnxn.cursor()
        query = "UPDATE Character SET clevel=('1') , experience=('0') , LevelUpPoint=400+400*Resets , Resets=Resets+1 , Strength=('8') , Dexterity=('8') , Vitality=('8') , Energy=('8') FROM Character join Memb_Stat on Character.Accountid = Memb_Stat.memb___id COLLATE Latin1_General_CS_AS JOIN MEMB_INFO ON Character.AccountID=MEMB_INFO.memb___id COLLATE Latin1_General_CS_AS WHERE clevel >= 400 and Money>('5000000') AND MEMB_STAT.ConnectStat = 0;"
        cursor.execute(query)
        cnxn.commit()
        cnxn.close()
        return f'[MU ARCANIS RESET] Done at {dt}'
        time.sleep(90)
    except Exception as e:
        return f'[MU ARCANIS RESET] Erro ao conectar ou executar a query, {dt} - {e}'

@bot.command(name='ranking')
async def top50_resets(ctx):
    top50 = getTop50Resets(cursor)
    message = ''
    if top50:
        for character in top50:
            message += f"#{character['position']} {character['name']} '{character['class']}' - Level: {character['level']} - Resets: {character['resets']}\n"
        await ctx.send(message)

@bot.command(name='pk')
async def top50_resets(ctx):
    top50 = getTop50Pks(cursor)
    message = ''
    if top50:
        for character in top50:
            message += f"#{character['position']} {character['name']} '{character['class']}' - Pk Count: {character['pkcount']} - Pk Level: {character['pklevel']} - Pk Time: {character['pktime']}\n"
        await ctx.send(message)

@tasks.loop(seconds=TIME_SEARCH_HACKER*60)
async def ds_anticheat(ANTICHEAT_CHANNEL):
    warehouse_hackers = findPossibleWarehouseHackers(cursor)
    inventory_hackers = findPossibleInventoryHackers(cursor)
    message = ''
    if warehouse_hackers:
        for hacker in warehouse_hackers:
            message += f"[MU ARCNANIS ANTI-CHEAT] Possible Warehouse FULL Item Hacker: AccountID <{hacker['account_id']}>"
    if inventory_hackers:
        for hacker in inventory_hackers:
            message += f"[MU ARCNANIS ANTI-CHEAT] Possible Inventory FULL Item Hacker: AccountID <{hacker['account_id']}>"
    await ANTICHEAT_CHANNEL.send(message)

@tasks.loop(seconds=TIME_RESET*60)
async def ds_autoreset(SYSTEM_CHANNEL):
    message = autoReset()
    await SYSTEM_CHANNEL.send(message)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    if bot.user.name == 'Arcanis':
        ANTICHEAT_CHANNEL = bot.get_channel(710496715001692247)
        SYSTEM_CHANNEL = bot.get_channel(710512149151350864)
        ds_anticheat.start(ANTICHEAT_CHANNEL)
        ds_autoreset.start(SYSTEM_CHANNEL)

bot.run(TOKEN)