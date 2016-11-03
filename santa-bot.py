import discord
import logging
import asyncio
import os.path
import configparser
import random

#set up debug log
debug = logging.getLogger('discord')
debug.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
debug.addHandler(handler)

#initialize config file
if os.path.isfile('participants.cfg') != True:
    with open('participants.cfg', 'x') as cfg:
        pass
config = configparser.ConfigParser()
config.read('participants.cfg')

#create null key if participants have not been initalized
if 'members' not in config.sections():
    config['members'] = {}

#initialize list of participants from config file
participants = [] 
for member in config['members']:
    participants.append(member)

#initialize instance of client class
client = discord.Client()

#handler for all on_message events
@client.event
async def on_message(message):
    #write all messages to a chatlog
    with open('chat.log','a+') as chatlog:
        chatlog.write('[' + message.author.name + ' in ' + message.channel.name + ' at ' + str(message.timestamp) + ']' + message.content + '\n')
    
    #ignore messages from the bot
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    if message.content.startswith('$$join'):
        #config['PARTICIPANTS'][message.author.name] = ''
        participants.append(message.author.name)
        config['PARTICIPANTS'][message.author.name] = None
        with open('participants.cfg') as configfile:
            config.write(configfile)
        print(participants)
        await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
    
    #command for admin to begin the secret santa
    #TODO: allow only ppl with admin permissions to run
    if message.content.startswith('$$start'):
        #for name in config['members']:
            #foo
    
    #allows a way to exit the bot
    #TODO: allow only ppl with admin permissions to run
    if message.content.startswith('$$shutdown'):
        await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
        raise KeyboardInterrupt

#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('token')