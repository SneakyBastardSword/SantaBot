import discord
import logging
import asyncio
import os.path
import configparser
import random

#class defining a participant and info associated with them
class Participant(object):
    def __init__(self, name, idstr, address = '', preferences = '', partner = '', partnerid = '', prtnr_addr = '', prtnr_prefs = ''):
        self.name = name                #string containing name of user
        self.idstr = idstr              #string containing id of user
        self.address = address          #string for user's address
        self.preferences = preferences  #string for user's gift preferences
        self.partner = partner          #string for name of partner
        self.partnerid = partnerid      #string for id of partner
        self.prtnr_addr = prtnr_addr    #string for address of partner
        self.prtnr_prefs = prtnr_prefs  #string for partner gift preferences

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

#store the keys in the cfg file to a dict of participants and store the number of participants to an int
usr_dict = {}
total_users = 0
with open('participants.cfg', 'r+') as cfg:
    for key in cfg['members']:
        usr_dict[key[0]] = (Participant(key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7], key[8]))
        total_users = total_users + 1

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
    elif message.content.startswith('$$join'):
        #initialize instance of participant class for the author 
        usr_dict[message.author.name] = (Participant(message.author.name, message.author.id))
        #write details of the class instance to config and increase total_users
        total_users = total_users + 1
        config['members'][total_users] = [message.author.name, message.author.id, '', '', '', '', '', '']
        with open('participants.cfg', 'a+') as configfile:
            config.write(configfile)
        
        #prompt user about inputting info
        await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
		await client.send_message(message.author, 'Please input your mailing address so your secret Santa can send you something!')
        await client.send_message(message.author, 'Use `$$setaddress` to set your mailing adress')
        await client.send_message(message.author, 'Use `$$setpreference` to set gift preferences for your secret santa')

    #accept adress of participants
    elif message.content.startswith('$$setaddress'):
        #add the input to the value in the user's class instance
        #FIXME: refactor for switch from usr_list to usr_dict
        for user in usr_dict:
            if user.idstr = message.author.id:
                user.preferences = message.content.replace('$$setaddress', '', 1)
                break
        #FIXME: refactor config file system for switch to Participant class
        #config['members'][message.author][1] = message.content.replace('$$setaddress', '', 1)
        #with open('participants.cfg', 'a+') as configfile:
        #    config.write(configfile)
        await client.send_message(message.author, 'Your address has been saved!')
    
    #accept gift preferences of participants
    elif message.content.startswith('$$setprefs')
        #add the input to the value in the user's class instance
        #FIXME: refactor for switch from usr_list to usr_dict
        for user in usr_dict:
            if user.idstr = message.author.id:
                user.preferences = message.content.replace('$$setpref', '', 1)
                break
        #FIXME: refactor config file system for switch to Participant class
        #config['members'][message.author][2] = message.content.replace('$$setpref', '', 1)
        #with open('participants.cfg', 'a+') as configfile:
        #    config.write(configfile)
        await client.send_message(message.author, 'Your gift preferences have been saved')

    #command for admin to begin the secret santa partner assignmenet
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    elif message.content.startswith('$$start'):
        #first ensure all users have all info submitted
        #FIXME: refactor for switch from usr_list to usr_dict
        for user in usr_dict:
            assign_error = False
            if user.address == '':
                await client.send_message(message.author, '```Error: ' + user.name + user.idstr + ' has not submitted their mailing address.```')
                assign_error = True
            if user.preferences == '': 
                await client.send_message(message.author, '```Error: ' + user.name + user.idstr + ' has not submitted their gift preferences.```')
                assign_error = True
        
        #only run if the above loop found no null values
        if assign_error:
           await client.send_message(message.author, '`Partner assignment cancelled.`')
        else:
            #FIXME: refactor for switch from usr_list to usr_dict
            partners = usr_dict
            #select a random partner for each participant
            for user in usr_dict:
                candidates = partners
                candidates.remove(user)
                partner = candidates[random.randint(0, available.len())]
                #remove user's partner from list of possible partners
                partners.remove(partner)
                
                #save the partner name, id, prefs and address to the participant's class instance
                user.partner = partner.name
                user.partnerid = partner.idstr
                user.prtnr_addr = partner.address
                user.prtnr_prefs = partner.preferences

                #tell participants who their partner is
                await client.send_message(user, partner.name + partner.idstr + 'Is your secret santa partner! Now find a gift and send it to them!')
                await client.send_message(user, 'Their mailing address is ' + partner.address)
                await client.send_message(user, 'Here are their gift preferences:')
                await client.send_message(user, partner.preferences)
    
    #allows a way to exit the bot
    #TODO: allow only ppl with admin permissions (i.e., @physics-official) to run
    elif message.content.startswith('$$shutdown'):
        await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
        raise KeyboardInterrupt
    
    #TODO: add a command for the bot to list off all participant names and id's, possibly only for admins

#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('token')