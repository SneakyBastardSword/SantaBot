import discord
import logging
import asyncio
import os.path
import configparser
import random

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

#initialize config file
if os.path.isfile('participants.cfg') != True:
    with open('participants.cfg', 'x') as cfg:
        pass
config = configparser.ConfigParser()
config.read('participants.cfg')

#create null key if [members] has not been initalized
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
    #TODO: ask for and store mailing address and gift preferences for each participant
    elif message.content.startswith('$$join'):
        participants.append(message.author)
        config['members'][message.author] = ''
        with open('participants.cfg') as configfile:
            config.write(configfile)
        await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
    
    #command for admin to begin the secret santa
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    #TODO: tell each participant the address and gift prefences of their partner
    elif message.content.startswith('$$start'):
        available = participants
        for user in config['members']:
            candidates = available
            candidates.remove(user)
            partner = candidates[random.randint(0, available.len())]
            available.remove(partner)
            config['members'][user] = available[partner]
            await client.send_message(user, partner.name + 'Is your secret santa partner! Now find a gift and send it to them!')
    
    #allows a way to exit the bot
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    elif message.content.startswith('$$shutdown'):
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