import discord
import logging
import asyncio
import os.path
import configparser
import random

class Participant(object):
    def __init__(self, user, address, ):
        self.foo = bar

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

#initialize config file
if os.path.isfile('participants.cfg') != True:
    with open('participants.cfg', 'x') as cfg:
        pass    #just need to create the file, no writing to be done yet
config = configparser.ConfigParser()
config.read('participants.cfg')

#create null key if [members] has not been initalized
if 'members' not in config.sections():
    config['members'] = {}
    #save to participants.cfg
    with open('participants.cfg', 'a+') as cfg:
        config.write(cfg)

#initialize list of participants from config file
participants = [] 
for member in config['members']:
    participants.append(member)

#initialize client class
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
        #append to list of participants
        participants.append(message.author)
        #add participant array to config and save to config file
        #array format: [0] is partner, [1] is address, [2] is gift preferences, [3] is partner's address, [4] is parnter's gift preference
        config['members'][message.author] = []  
        with open('participants.cfg', 'a+') as configfile:
            config.write(configfile)
        await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
		await client.send_message(message.author, 'Please input your mailing address so your secret Santa can send you something!')
        await client.send_message(message.author, 'Use `$$setaddress` to designate your mailing adress')
        await client.send_message(message.author, 'Use `$$setpreference` to set gift preferences for your secret santa'

    #command for admin to begin the secret santa
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    #TODO: tell each participant the address and gift prefences of their partner
    elif message.content.startswith('$$start'):
        partners = participants
        #select a random partner for each participant
        for user in config['members']:
            candidates = partners
            candidates.remove(user)
            partner = candidates[random.randint(0, available.len())]
            #remove user's partner from list of partners
            partners.remove(partner)
            #save partner in config file
            config['members'][user][0] = available[partner]
            with open('participants.cfg', 'a+') as configfile:
                config.write(configfile)
            
            #tell participants who their partner is
            await client.send_message(user, partner.name + 'Is your secret santa partner! Now find a gift and send it to them!')
    
    #allows a way to exit the bot
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    elif message.content.startswith('$$shutdown'):
        await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
        raise KeyboardInterrupt

    #accept adress of participants
    elif message.content.startswith('$$setaddress'):
        user_address = message.content
        config['members'][message.author][1] = user_address.replace('$$setaddress', '', 1)
        with open('participants.cfg', 'a+') as configfile:
            config.write(configfile)
    
    elif message.content.startswith('$$setpreference')
#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('token')