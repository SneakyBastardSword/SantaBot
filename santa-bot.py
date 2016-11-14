import discord
import logging
import asyncio
import os.path
import configparser
import random

#class defining a participant and info associated with them
class Participant(object):
    def __init__(self, name, idstr, usrnum, address = '', preferences = '', partner = '', partnerid = '', prtnr_addr = '', prtnr_prefs = ''):
        self.name = name                #string containing name of user
        self.idstr = idstr              #string containing id of user
        self.usrnum = usrnum            #int value referencing the instance's location in participants.cfg and usr_list
        self.address = address          #string for user's address
        self.preferences = preferences  #string for user's gift preferences
        self.partner = partner          #string for name of partner
        self.partnerid = partnerid      #string for id of partner
        self.prtnr_addr = prtnr_addr    #string for address of partner
        self.prtnr_prefs = prtnr_prefs  #string for partner gift preferences
    
    #returns whether the user has set an address
    def addressIsSet():
        if self.address = '':
            return False
        else:
            return True
    
    #returns whether the user has set gift preferences
    def prefIsSet():
        if self.preferences = '':
            return False
        else:
            return True

#takes a discord user ID string and list of participant objects, and returns the participant object with matching id, raising a ValueError if object does not exist
def getParticipantObject(usrid, usrlist = usr_list):
    person_found = False
    for person in usrlist:
        if person.idstr = usrid:
            person_found = True
            return person
    if not person_found:
        return False

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

#store the keys in the cfg file to a list of participant class instances and store the number of participants to an int
usr_list = []
total_users = 0
with open('participants.cfg', 'r+') as cfg:
    for key in cfg['members']:
        usr_list[total_users] = Participant(key[0], key[1], total_users, key[2], key[3], key[4], key[5], key[6], key[7], key[8])
        total_users = total_users + 1

#initialize client class instance 
client = discord.Client()

#handler for all on_message events
@client.event
async def on_message(message):
    #write all messages to a chatlog
    with open('chat.log','a+') as chat_log:
        chat_log.write('[' + message.author.name + message.author.id + ' in ' + message.channel.name + ' at ' + str(message.timestamp) + ']' + message.content + '\n')
    
    #ignore messages from the bot itself
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    elif message.content.startswith('$$join'):
        #check if message author has already joined
        if getParticipantObject(message.author.id, usr_list) != False:
            await client.send_message('`Error: You have already joined!`')
        else:
            #initialize instance of participant class for the author 
            usr_list[message.author.name] = (Participant(message.author.name, message.author.id))
            #write details of the class instance to config and increase total_users
            total_users = total_users + 1
            config['members'][str(total_users)] = [message.author.name, message.author.id, '', '', '', '', '', '']
            with open('participants.cfg', 'a+') as cfg:
                config.write(cfg)
            
            #prompt user about inputting info
            await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
            await client.send_message(message.author, 'Please input your mailing address so your secret Santa can send you something!')
            await client.send_message(message.author, 'Use `$$setaddress` to set your mailing adress')
            await client.send_message(message.author, 'Use `$$setpreference` to set gift preferences for your secret santa')
    
    #accept adress of participants
    elif message.content.startswith('$$setaddress'):
        #check if author has joined the exchange yet
        if not getParticipantObject(message.author.id):
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
        else:
            #add the input to the value in the user's class instance
            person = getParticipantObject(message.author.id)
            person.preferences = message.content.replace('$$setaddress', '', 1)
            #save to config file
            config['members'][str(person.usrnum)][3] = message.content.replace('$$setaddress', '', 1)
            with open('participants.cfg', 'a+') as cfg:
                config.write(cfg)
            await client.send_message(message.author, 'Your address has been saved!')
    
    #accept gift preferences of participants
    elif message.content.startswith('$$setprefs')
        #check if author has joined the exchange yet
        if not getParticipantObject(message.author.id):
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
        else:
            #add the input to the value in the user's class instance
            getParticipantObject(message.author.id, usr_list).preferences = message.content.replace('$$setpref', '', 1)
            #save to config file
            config['members'][str(person.usrnum)][4] = message.content.replace('$$setpref', '', 1)
            with open('participants.cfg', 'a+') as cfg:
                config.write(cfg)
            await client.send_message(message.author, 'Your gift preferences have been saved')
    
    #command for admin to begin the secret santa partner assignmenet
    elif message.content.startswith('$$start'):
        #only allow people with admin permissions to run
        if 'admin' in permissions_for(message.author): 
            #first ensure all users have all info submitted
            all_fields_complete = True
            for user in usr_list:
                #check if no null values in address or prefs of participants
                if user.addressIsSet() and user.prefIsSet:
                    pass
                else:
                    all_fields_complete = False
                    await client.send_message(message.author, '`Error: ' + user.name + ' has not submitted either a mailing address or gift preferences.`')
            #select a random partner for each participant if above loop found no empty values
            if all_fields_complete:
                for user in usr_list:
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
                    await client.send_message(user, partner.name + partner.idstr + 'Is your secret santa partner! Now pick out a gift for them and send it to them!')
                    await client.send_message(user, 'Their mailing address is ' + partner.address)
                    await client.send_message(user, 'Here are their gift preferences:')
                else:
                    await client.send_message(message.author, '`Partner assignment canceled: participant info incomplete.`')
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    #allows a way to exit the bot
    elif message.content.startswith('$$shutdown'):
        #only allow ppl with admin permissions to run
        if 'admin' in permissions_for(message.author):
            await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
            raise KeyboardInterrupt
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #lists off all participant names and id's
    elif message.content.startswith('$$listparticipants'):
        if total_users = 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        else:
            message = '```The following people are signed up for the secret santa exchange:\n'
            for user in usr_list:
                message.append(user.name + user.idstr + '\n')
            message.append('Use `$$join` to enter the exchange.```')
            await client.send_message(message.channel, message)
    
    #lists total number of participants
    elif message.content.startswith('$$totalparticipants'):
        if total_users = 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        elif total_users = 1:
            await client.send_message(message.channel, '1 person has signed up for the secret santa exchange. Use `$$join` to enter the exchange.')
        else:
            await client.send_message(message.channel, 'A total of ' + total_users + ' users have joined the secret santa exchange so far. Use `$$join` to enter the exchange.')

#print message when client is connected
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord connection abstraction
client.run('token')