import discord
import logging
import asyncio
import datetime
import os.path
import configparser

#set up debug log
debug = logging.getLogger('discord')
debug.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
debug.addHandler(handler)

#initialize config file
config = configparser.ConfigParser()
#create null key if participants have not been initalized
if 'PARTICIPANTS' not in config:
    config['PARTICIPANTS'] = {}

#initialize list of participants from config file
participants = [] 
for member in config[PARITCIPANTS]:
    participants.append(member)

#initialize instance of client class
client = discord.client

#handler for all on_message events
@client.event
async def on_message(message):
    #write all messages to a chatlog
    with open('chat.log','a+') as chatlog:
        await chatlog.write('[' + message.author.name + ' in ' + message.channel + ' at ' + message.timestamp + ']' + message.content)
    
    #ignore messages from the bot
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    if message.content.startswith('$$join'):
        config['PARTICIPANTS'][message.author.name] = ''
        await participants.append(message.author)
        await client.send_message(message.channel, '{0.author.mention} Has been added to the OfficialFam Secret Santa lottery!')
    
    if message.content.startswith('$$start')
#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('MjMzMjYyNzY4NjUwODQ2MjA4.CusdJQ.7l4wOKT-mtSVDu8JUUXKeHJr_F8')