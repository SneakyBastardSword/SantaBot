import discord
import logging
import asyncio
import os.path
import configparser
import random

#class defining a participant and associated with them
class Participant(object):
    def __init__(self, idstr):
        self.idstr = idstr
        self.address = ''
        self.preferences = ''
        self.partner = ''
        self.prtnr_addr = ''
        self.prtnr_prefs = ''

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
config.read_file('participants.cfg')

#initialize client class instance 
client = discord.Client()

#handler for all on_message events
@client.event
async def on_message(message):
    #write all messages to a chatlog
    with open('chat.log','a+') as chatlog:
        chatlog.write('[' + message.author.name + ' in ' + message.channel.name + ' at ' + str(message.timestamp) + ']' + message.content + '\n')
    
    #ignore messages from the bot itself
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    #TODO: ask for and store mailing address and gift preferences for each participant
    elif message.content.startswith('$$join'):
        #initialize instance of participant class for the author 
        str(message.author.name) = Participant(message.author.id)
        config['members'][message.author.name] = 
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
    
    elif message.content.startswith('$$setpref')
        message.author.id = 
#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('token')