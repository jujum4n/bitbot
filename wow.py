import urllib.request

import json
import csv
import discord
from utils import get_token
api_key = get_token('wow')
servers = ['Emerald%20Dream']
item_list = 'missing.csv'
char_name = 'Felkush'

#Decription: Helper function Given a member and a string has the bot say it
async def say(bot, message, value_to_say):
    await bot.send_message(message.channel, value_to_say) 

def get_auction_url(resturl):
    response = urllib.request.urlopen(resturl)
    data = response.read()
    text = data.decode('utf-8')
    data = json.loads(text)
    return data
    
def get_auction_data(auction_json_url):
    response = urllib.request.urlopen(auction_json_url)
    data = response.read()
    text = data.decode('utf-8')
    data = json.loads(text)
    return data

def get_expired_ids(filename):
    expired_ids = []
    expired_names = []
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            expired_ids.append(row[1])
            expired_names.append(row[0])
    return expired_ids, expired_names


async def check_server(bot, message, servername):
    expired_ids, expired_names = get_expired_ids(item_list)
    whole_editable ='```+----------Rare Auction Finder - By: juju - (Do not steal)----------+```\n'
    # Map the ID's to integers
    expired_ids = list(map(int, expired_ids))
    await bot.send_message(message.channel, whole_editable)
    auction_rest_url = 'https://us.api.battle.net/wow/auction/data/' + servername +'?locale=en_US&apikey=' + api_key

    auction_url = get_auction_url(auction_rest_url)
    auction_url = auction_url['files'][0]['url']

    auctions = get_auction_data(auction_url)
    auctions = auctions['auctions']

    found_list = []
    for auction in auctions:
        if auction['item'] in expired_ids:
            name_position = expired_ids.index(auction['item'])
            found_list.append(auction['item'])
            if auction['item'] == 22682:
                await bot.send_message(message.channel, '***YO JUJU I FOUND A FROZEN RUNE***')
                await bot.send_message(message.channel, '***YO JUJU I FOUND A FROZEN RUNE***')
                await bot.send_message(message.channel, '***YO JUJU I FOUND A FROZEN RUNE***')
    uglystr = ''
    for item in found_list:
        uglystr+=str(item)+','
    uglystr = uglystr[:-1]
    await bot.send_message(message.channel, str(len(found_list)) + ' items on Emerald Dream - TSM Import:\n' + uglystr)
    file = open("rares.file", "w")
    for item in found_list:
        file.write('https://www.tradeskillmaster.com/items/'+str(item)+'\n')
    file.close()

