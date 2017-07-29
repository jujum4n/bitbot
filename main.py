# Description: Custom Discord Bot written in Python
# Dependencies: discord.py and Python 3.5 along with Ubuntu
# Author: Juju

import discord
import asyncio
import json
import time
import random
import redis
from random import randint, choice
from race import Race, Racer, checkered_flag, all_carts, get_rand_cart
from utils import p, get_token, msg
from pokeiv import get_all_iv_range
from db import rset, rget, connect
from cmds import get_btc_price, get_giphy_trending, get_qod, get_xkcd, flip, bing_search
from wow import check_server
# Create a bot client
bot = discord.Client()
# Get a token so you can login
token = get_token('cert')

# Race variables
race_editable = ''
pregame_editable = ''
pregame = False
r = ''
in_race = []

currency_emoji = ':gem:'

# Variables needed for our redis server
IP = '0.0.0.0'
PORT = 6379
PASS = ''
rc = redis.Redis(host=IP, port=PORT, password=PASS)
if rc:
    msg('Redis Connection Success!')

db_flush = False

if db_flush == True:
    rc.flushall()

#Description: List of async tasks to run in the on ready event
async def tasks(): #sync_offset
    await asyncio.wait([
            bg_reward_bits_loop()
        ])



# Define an event to happen when the Bot is Ready
@bot.event
async def on_ready():
    msg('Login Success!')
    msg('Username: ' + bot.user.name)
    msg('Connected to Servers:')
    for server in bot.servers:
        msg(' - '+server.name)
    msg('Starting async loops')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(await tasks())
    loop.close()


#Decription: Helper function Given a member and a string has the bot say it
async def say(bot, message, value_to_say):
    await bot.send_message(message.channel, value_to_say) 



# Define an event to happen when the bot receives a message
@bot.event
async def on_message(message):
    # Returns most popular gif currently
    if message.content.startswith('`giphy'):
        giphyurl = get_giphy_trending()
        await say(bot, message, giphyurl)
    # Returns latest xkcd comic
    if message.content.startswith('`xkcd'):
        text = get_xkcd()
        await say(bot, message, 'Current xkcd \n' + text)
    # Returns a Quote of the Day
    if  message.content.startswith('`quote'):
        text = get_qod()
        await say(bot, message, text)
    # Returns a list of all the commands available
    if  message.content.startswith('`help') or message.content.startswith('`commands'):
        msgtosend = 'bitbot v0.1 - by: juju - commands must start with: **`** \n--------------------------------------------------------------------------------------\n**$$$** - Shows your :gem: balance\n**items** - lists all purchasable items\n**gamble <amount>** - Wager a specific amount\n**minercalc** - Lets you know max # miners you can buy\n**buy <item> <quantity>** - buys a given item at a specific quantity\n**race** - starts a race, type: **jr** - to join a race\n**btc** - gets current bitcoin price\n**8ball** - gets a response to question\n**flip** - flips a coin\n**quote** - gets quote of the day\n**xkcd** - gets recent xkcd\n**giphy** - gets current trending giphy\n**img** - returns bing image search for given keyword\n--------------------------------------------------------------------------------------\n'
        await say(bot, message, msgtosend)
    # Returns coinbase bitcoin price
    if message.content.startswith('`btc'):
        text = get_btc_price()
        await say(bot, message, text)
    # Returns an 8ball response
    if message.content.startswith('`8ball'):
        choices = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes, definitely', 'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later', 'Better not tell you now', '¯\_(ツ)_/¯', 'Concentrate and ask again', """Don't count on it""", 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
        rand_num = randint(0, 19)
        if message.server==None:
            await say(bot, message, choices[rand_num])
        else:
            await say(bot, message, choices[rand_num])
    # someone wants to see all buyable items
    if message.content.startswith('`items'):
        msgtosend = 'item list\n--------------------------------------------------------------------------------------\nminer - cost 30bits\n--------------------------------------------------------------------------------------'
        await say(bot, message, msgtosend)
    # Returns either heads or tails
    if message.content.startswith('`flip'):
        result = flip()
        messagetosend = '-everything turns to slow motion as bitbot flips a coin into the air, it dramatically lands on ' + result + '-'
        await say(bot, message, messagetosend)
    # Returns an image from bing given a keyword
    if  message.content.startswith('`img'):
        items = message.content.replace('`img ', '')
        returnurl = bing_search(items)
        memeimg = (returnurl['d']['results'][0]['MediaUrl'])
        await say(bot, message, memeimg)
    #await bot.edit_message(tmp, 'You have {} messages.'.format(counter))
    if message.content.startswith('`iv'):
        ivs = get_all_iv_range(message.content)
        tosay = ''
        for item in ivs:
            tosay += str(item) + '\n'
            
        await say(bot, message, tosay)
    # If the users command starts with race
    if message.content.startswith('`race'):
        #Get our global race variables needed for jr command
        global pregame
        global in_race
        global pregame_editable
        global r
        # If the pregame has not been started
        # And if their is no one in our in_race global
        if pregame == False and len(in_race)==0:
            mycart = message.content.split(' ')
            add_juju = False
            if message.author.name != 'juju':
                jujuol = discord.utils.find(lambda m: m.name == 'juju', message.server.members)
                if jujuol.status == discord.Status.online:
                    add_juju = True
            # Try to get a cart from the user otherwise pick a random cart from our cart list
            if len(mycart) > 1 and mycart[1] in all_carts:
                mycart = mycart[1]
            else:
                mycart = random.choice(all_carts)
            # Create a race with the person who started the race and with either their cart or a random cart from our list
            r = Race(message.author.name, mycart)
            in_race.append(message.author.name)
            # Race has started pregame has begun
            r.started = True
            place = 0
            pregame = True
            # Our global editable message string, updates as time goes on
            pregame_editable = await bot.send_message(message.channel, 'Race Starting - `jr to join - 30 seconds left to join race')
            # Let the person who started the race know they are in the race and which cart they have
            await say(bot, message, message.author.name +' has joined the race as: ' + mycart)
            
            # if juju is online just automatically add him
            if add_juju:
                newcart = random.choice(all_carts)
                in_race.append('juju')
                jujucart = random.choice(all_carts)
                m = Racer('juju', jujucart)
                r.add_racer(m)
                await say(bot, message, 'juju has auto-joined the race as: ' + jujucart)
            # Wait 30 seconds for people to join, then remove the join message
            for x in range(1,30):
                await asyncio.sleep(1)
                await bot.edit_message(pregame_editable, 'Race Starting Soon - type: `jr to join - '+ str(30 - x) +' seconds :checkered_flag:' + (30 - x)*'.'+':frog::ok_hand:')
            await bot.delete_message(pregame_editable)
            
            # For every racer in our race object add them to our in_race variable
            for racer in r.racers:
                in_race.append(racer.name)
            
            # Update our race every second possibly, up to 30 times
            for x in range(1, 30):
                pstring ='`Race Wars - By: juju`\n\n'
                # For every racer in our race
                for racer in r.racers:
                    # If the racer is finished
                    if racer.finished == True:
                        # Check to see if the racer is in our races places list if they are print a new message for them
                        if racer.name in r.places:
                            pstring+=racer.race_finished+'\n'
                        # If they are finished but not in the races places list append them to this list and create a string to print out
                        if racer.name not in r.places:
                            r.places.append(racer.name)
                            racer.finished = True
                            racer.percentage = 100
                            place = place+1
                            racer.place = place
                            place_display = ''
                            if racer.place == 1:
                                place_display = '1st - Winner'
                            if racer.place == 2:
                                place_display = '2nd'
                            if racer.place == 3:
                                place_display = '3rd'
                            if racer.place == 4:
                                place_display = '4th'
                            if racer.place == 5:
                                place_display = '5th'
                            if racer.place == 6:
                                place_display = '6th'
                            if racer.place == 7:
                                place_display= '7th'
                            racer.race_finished =  checkered_flag + ' ' + racer.cart + ' ' + racer.name + ' - ' + place_display
                            # Try to remove the racer from our in_race object
                            try:
                                in_race.remove(racer.name)
                            # Just an exception incase
                            except:
                                print('racer already removed')
                            pstring+=racer.race_finished + '\n'
                    # If the racer is not finished, go ahead and move them and create a string to display with their movement
                    if racer.finished == False:
                        r.move_racer(racer)
                        pstring+=racer.race_display+'\n'
                # If it is the very first time you display the race message
                if x is 1:
                    race_editable = await bot.send_message(message.channel, pstring)
                # Otherwise edit the message since you already sent it to the server
                else:
                    await bot.edit_message(race_editable, pstring)
                # Wait 1 second
                await asyncio.sleep(1)
                # If their is no one left in the race, break out of our forloop
                if len(in_race) == 0:
                    break
            # For all the racers set the place strings to print out at the end
            for racer in r.racers:
                reward = 0
                placestr =''
                if racer.place == 1:
                    reward = 500
                    placestr = '1st'
                if racer.place == 2:
                    reward = 250
                    palcestr = '2nd'
                if racer.place == 3:
                    reward = 125
                    placestr = '3rd'
                if racer.place == 4:
                    reward = 62
                    placestr = '4th'
                if racer.place == 5:
                    reward = 31
                    placestr ='5th'
                await say(bot, message, racer.name+' won ' + str(reward) + ':gem: for ' + placestr + ' place')
                rc.incr(racer.name+':bits_total', amount=reward)
             # Get a random picture to display at the end of the race
            giflist = ['https://i.imgur.com/MRn00m5.gif', 
            'https://38.media.tumblr.com/d5f10d02c8bae9f9e98dc1f9bdd02852/tumblr_n8hr5mJag71r5y20oo1_r1_500.gif', 
            'https://cdn0.vox-cdn.com/thumbor/z2xzQoO-epkP7J4NOjkmwRPj7QM=/cdn0.vox-cdn.com/uploads/chorus_asset/file/3558378/ff1.0.gif', 
            'http://imagesmtv-a.akamaihd.net/uri/mgid:file:http:shared:mtv.com/news/wp-content/uploads/2015/04/tumblr_mrf491Riev1qcga5ro1_500-1430142380.gif', 
            'https://i.imgur.com/BukjVKV.gif', 
            'https://media.giphy.com/media/3oEjHAUOqG3lSS0f1C/giphy.gif', 
            'https://metvnetwork.s3.amazonaws.com/iIzD9-1461082384-3428-list_items-wacky_slag.gif',
            'https://i.kinja-img.com/gawker-media/image/upload/uts1p7ryuscst14fqxxx.jpg',
            'https://i.ytimg.com/vi/3hx-hEWl10c/maxresdefault.jpg',
            'http://i0.kym-cdn.com/photos/images/newsfeed/000/506/223/2ab.gif',
            'http://i3.kym-cdn.com/photos/images/facebook/000/148/747/sonic_is_fast_by_heyitskurt-d3ew3q6.png',
            'http://ci.memecdn.com/106/6924106.jpg',
            'https://41.media.tumblr.com/ba9d9fc7aba9b951f1b10e42b16bef5f/tumblr_ni9cqwZKLO1t2axlxo1_500.jpg',
            'https://i.imgur.com/zjrv38V.png',
            'http://i3.kym-cdn.com/photos/images/facebook/000/545/119/ceb.png',
            'http://wordpress.carthrottle.com/wp-content/uploads/2013/04/Car-darts.gif',
            'https://barkpost-assets.s3.amazonaws.com/wp-content/uploads/2013/08/car.gif',
            'http://www.best-gif.com/wp-content/uploads/2013/10/funny-gifs-Im-late-at-woooork.gif',
            'https://67.media.tumblr.com/2c2902e46556cf6ee41e9b442cbbebd1/tumblr_n5fw4b2Isb1svxaato1_400.gif',
            'https://medschoolzombie.files.wordpress.com/2014/05/ricky-bobby-if-you-aint-first-e1303710617483.jpg',
            'https://s-media-cache-ak0.pinimg.com/736x/67/77/f4/6777f4ad062b8a42a770d2eaf3c1c571.jpg',
            'https://monteelopez.files.wordpress.com/2013/06/66984_o.gif',
            'http://www.dan-dare.org/Dan%20FRD/MeanMachineAni.gif',
            'https://67.media.tumblr.com/ac43622ff34d4ddbe94ce37c27d619be/tumblr_n8pnrm6AA61rvcrndo1_1280.gif',
            'https://metvnetwork.s3.amazonaws.com/iIzD9-1461082384-3428-list_items-wacky_slag.gif',
            'https://cdn1.vox-cdn.com/thumbor/CQaHIpYoXdGCQ72eeuiBvwpplWM=/cdn0.vox-cdn.com/uploads/chorus_asset/file/6617731/giphy.gif',
            'http://m.memegen.com/wzv5l0.jpg',
            'http://s2.quickmeme.com/img/86/861417aa4d59deceb3545121425eb8762779c67a21062a44b35350dfd5babc82.jpg',
            'http://www.relatably.com/m/img/fast-memes/b34ae8cab6894efa64d58ed2238e090c38cebe601a9cd92cf6d61d813f22529d.jpg'
            ]
           
            gif = randint(0, len(giflist))
            # Update the race message with the Gif
            await bot.edit_message(race_editable, pstring+'\n'+giflist[gif])
            # Fix our globals
            pregame = False
            in_race=[]
            pregame_editable = ''
            race_editable = ''
    
    if message.content.startswith('`jr'):
        # If our pregame has started, and their is a race, and the person trying to join the race is not in it already
        if pregame == True and r and message.author.name not in in_race:
            mycart = message.content.split(' ')
            # If they have a cart and its in the list of carts
            if len(mycart) > 1 and mycart[1] in all_carts:
                mycart = mycart[1]
                # Create a racer and add them to our race trackers
                racertoadd = Racer(message.author.name, mycart)
                r.add_racer(racertoadd)
                in_race.append(message.author.name)
                await say(bot, message, message.author.name +' has joined the race as: ' + mycart)
            # Otherwise they did not input a cart, add them to the race and give them a random cart
            else:
                mycart = random.choice(all_carts)
                racertoadd = Racer(message.author.name, mycart)
                r.add_racer(racertoadd)
                in_race.append(message.author.name)
                await say(bot, message, message.author.name +  ' has joined the race as: ' + mycart)

    # If the message content starts with the word grant
    if message.content.startswith('`grant'):
        # Take the command that you got and split it at all the places where their is a space
        command = message.content.split(' ')
        # If the author of the message is juju 
        if message.author.name == 'juju' and message.author.id == '121484848404758530':
            if command[1]:
                if command[2]:
                    member = discord.utils.find(lambda m: m.name == command[1], message.server.members)
                    if member:
                        rc.incr(member.name+':bits_total', command[2])
                        await say(bot, message, 'Granted '+ member.name +' '+ "{:,}".format(int(command[2]))+':gem:')

    # If the user is trying to gamble bits
    if message.content.startswith('`gamble'):
        command = message.content.split(' ')
        # If they have a second parameter
        if command[1]:
            # Get how many bits they have
            total = rc.get(message.author.name + ':bits_total')
            # If they 
            if total != None and command[1]!='all' and command[1]!='max' and int(command[1])>0:
                if int(command[1]) <= int(total):
                    randnum = random.randint(1, 100)
                    if randnum >=51:
                        rc.incr(message.author.name+':bits_total', amount=int(command[1]))
                        await say(bot, message, 'Roll: ' + str(randnum) + ' - You won ' + "{:,}".format(int(command[1])) + ':gem:')
                    else:
                        await say(bot, message, 'Roll: ' + str(randnum) + ' - You lost ' + "{:,}".format(int(command[1])) + ':gem:')
                        rc.decr(message.author.name+':bits_total', amount=int(command[1]))
        if command[1] == 'all' or command[1] == 'max':
            await say(bot, message, '!!!This command has been depricated use: gambleall, gamblemax, or use the aptly named: ihaveaproblem command')
            await say (bot, message, '-bitbot looks directly at both LazyBones and Splatzilla-')
        if total == None or int(command[1]) > int(total):
            await say(bot, message, 'You only have: ' + "{:,}".format(int(total)) + ':gem:')
        if int(command[1])<=0:
            await say(bot, message, '-bitbot glares intently at Prophet then grumbles: negative numbers nice one man-')
    # Checks the users Bits value
    if message.content.startswith('$$$') or message.content.startswith('`$$$') or message.content.startswith('`$'):
        total = rc.get(message.author.name + ':bits_total')
        if total == None:
            print(message.author.name + ' needs to be registered')
            rc.set(message.author.name + ':bits_total', '1')
            await say(bot, message, message.author.name + ' - ' + "{:,}".format(int(1)) + ':gem:')
        await say(bot, message, message.author.name + ' - ' + "{:,}".format(int(total)) + ':gem:')

    if message.content.startswith('`gambleall') or message.content.startswith('`gamblemax') or message.content.startswith('`ihaveaproblem'):
        command = message.content.split(' ')
        total = rc.get(message.author.name + ':bits_total')
        # If they 
        if total != None:
            randnum = random.randint(1, 100)
            if randnum >=51:
                rc.incr(message.author.name+':bits_total', amount=int(total))
                await say(bot, message, 'Roll: ' + str(randnum) + ' - You won: ' + "{:,}".format(int(total)) + ':gem:')
            else:
                await say(bot, message, 'Roll: ' + str(randnum) + ' - You lost: ' + "{:,}".format(int(total)) + ':gem:')
                rc.decr(message.author.name+':bits_total', amount=int(total))
    if message.content.startswith('`rareauctions'):
        await check_server(bot, message, 'Emerald%20Dream')

#Description: Loop example
async def bg_reward_bits_loop():
    global rc
    #Sleep value for reward loop in seconds, love being rewarded for sleeping
    sleep = 60
    while True:
        for server in bot.servers:
            #For every member connected to the server
            for member in server.members:
                if member.status == discord.Status.online:
                    total = rc.get(member.name+':bits_total')
                    if total == None:
                        print(member.name + ' needs to be registered')
                        rc.set(member.name+':bits_total', '0')
                    else:
                        pm_total = rc.get(member.name + ':bits_pm')
                        if pm_total == None:
                            rc.set(member.name + ':bits_pm', '1')
                            rc.incr(member.name+':bits_total')
                        else:
                            rc.incr(member.name+':bits_total', amount=int(pm_total))
        msg('Sleeping ' + str(int(sleep)/60) + ' minute(s) in: ' + str(bg_reward_bits_loop.__name__))
        await asyncio.sleep(sleep)

bot.run(token)