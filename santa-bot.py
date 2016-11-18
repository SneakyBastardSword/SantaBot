import logging
import asyncio
import os.path
import random
import discord
from configobj import ConfigObj

class Participant(object):
    """class defining a participant and info associated with them"""
    def __init__(self, name, idstr, usrnum, address='', preferences='', partnerid=''):
        self.name = name                #string containing name of user
        self.idstr = idstr              #string containing id of user
        self.usrnum = usrnum            #int value referencing the instance's location in usr_list
        self.address = address          #string for user's address
        self.preferences = preferences  #string for user's gift preferences
        self.partnerid = partnerid      #string for id of partner
    
    def address_is_set(self):
        """returns whether the user has set an address"""
        if self.address == '':
            return False
        else:
            return True
    
    def pref_is_set(self):
        """returns whether the user has set gift preferences"""
        if self.preferences == '':
            return False
        else:
            return True

#initialize config file
if not os.path.exists('./files/participants.cfg'):
    config = ConfigObj('./files/participants.cfg')
    config['programData'] = {'exchange_started': False, 'discord_token': 'token'}
    config['members'] = {}
    config.write()
else:
    config = ConfigObj('./files/participants.cfg')

#initialize data from config file
usr_list = []
total_users = 0
exchange_started = config['programData']['exchange_started']
print(exchange_started)
for key in config['members']:
    total_users = total_users + 1
    usr_list.append(Participant(key[0], key[1], total_users, key[2], key[3], key[4]))

def user_is_participant(usrid, usrlist=usr_list):
    """Takes a discord user ID string and returns whether
    a user with that ID is in usr_list"""
    result = False
    for person in usrlist:
        if person.idstr == usrid:
            result = True
            break
    return result

def get_participant_object(usrid, usrlist=usr_list):
    """takes a discord user ID string and list of
    participant objects, and returns the first
    participant object with matching id."""
    for person in usrlist:
        if person.idstr == usrid:
            return person
            break

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='./files/debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

#initialize client class instance
client = discord.Client()

#handler for all on_message events
@client.event
async def on_message(message):
    #declare global vars
    global usr_list
    global total_users
    global exchange_started
    #write all messages to a chatlog
    with open('./files/chat.log', 'a+') as chat_log:
        chat_log.write('[' + message.author.name + message.author.id + ' in ' + message.channel.name + ' at ' + str(message.timestamp) + ']' + message.content + '\n')
    
    #ignore messages from the bot itself
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    elif message.content.startswith('$$join'):
        #check if message author has already joined
        if user_is_participant(message.author.id):
            await client.send_message(message.channel, '`Error: You have already joined.`')
        #check if the exchange has already started
        elif exchange_started == True:
            print(exchange_started)
            await client.send_message(message.channel, '`Error: Too late, the gift exchange is already in progress.`')
        else:
            #initialize instance of participant class for the author
            usr_list.append(Participant(message.author.name, message.author.id, total_users))
            #write details of the class instance to config and increment total_users
            total_users = total_users + 1
            config['members'][str(total_users)] = [message.author.name, message.author.id, total_users]
            config.write()
            
            #prompt user about inputting info
            await client.send_message(message.channel, message.author.mention + ' Has been added to the OfficialFam Secret Santa exchange!')
            await client.send_message(message.author, 'Please input your mailing address so your secret Santa can send you something!')
            await client.send_message(message.author, 'Use `$$setaddress` to set your mailing adress')
            await client.send_message(message.author, 'Use `$$setpreference` to set gift preferences for your secret santa')
    
    #accept address of participants
    elif message.content.startswith('$$setaddress'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            user = get_participant_object(message.author.id)
            user.address = message.content.replace('$$setaddress', '', 1)
            #save to config file
            config['members'][str(user.usrnum)][3] = user.address
            config.write()
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #accept gift preferences of participants
    elif message.content.startswith('$$setprefs'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            user = get_participant_object(message.author.id)
            user.preferences = message.content.replace('$$setpref', '', 1)
            #save to config file
            config['members'][str(user.usrnum)][4] = user.preferences
            config.write()
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #command for admin to begin the secret santa partner assignmenet
    elif message.content.startswith('$$start'):
        #FIXME:only allow people with admin permissions to run
        #if 'admin' in client.permissions_for(message.author):
        #first ensure all users have all info submitted
        all_fields_complete = True
        for user in usr_list:
            #check if no null values in address or prefs of participants
            if user.address_is_set() and user.pref_is_set():
                pass
            else:
                all_fields_complete = False
                await client.send_message(message.author, '`Error: ' + user.name + ' has not submitted either a mailing address or gift preferences.`')
        
        #select a random partner for each participant if above loop found no empty values
        if all_fields_complete:
            partners = usr_list
            for user in usr_list:
                candidates = partners
                candidates.remove(user)
                partner = candidates[random.randint(0, len(candidates) - 1)]
                #remove user's partner from list of possible partners
                partners.remove(partner)
                #save the partner id to the participant's class instance
                user.partnerid = partner.idstr
                #save to config file
                config['users'][str(user.usrnum)][5] = user.partnerid
                config.write()

                #tell participants who their partner is
                await client.send_message(user, partner.name + partner.idstr + 'Is your secret santa partner! Now pick out a gift for them and send it to them!')
                await client.send_message(user, 'Their mailing address is ' + partner.address)
                await client.send_message(user, 'Here are their gift preferences:')
            #set exchange_started + assoc. cfg value to True
            exchange_started = True
            config['programData']['exchange_started'] = True
        else:
            await client.send_message(message.author, '`Partner assignment canceled: participant info incomplete.`')
        #else:
            #await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #allows a way to exit the bot
    elif message.content.startswith('$$shutdown'):
        #FIXME: only allow ppl with admin permissions to run
        #if 'admin' in client.permissions_for(message.author):
        await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
        raise KeyboardInterrupt
        #else:
        #    await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #lists off all participant names and id's
    elif message.content.startswith('$$listparticipants'):
        if total_users == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        else:
            msg = '```The following people are signed up for the secret santa exchange:\n'
            for user in usr_list:
                msg = msg + user.name + user.idstr + '\n'
            msg = msg + 'Use `$$join` to enter the exchange.```'
            await client.send_message(message.channel, msg)
    
    #lists total number of participants
    elif message.content.startswith('$$totalparticipants'):
        if total_users == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        elif total_users == 1:
            await client.send_message(message.channel, '1 person has signed up for the secret santa exchange. Use `$$join` to enter the exchange.')
        else:
            await client.send_message(message.channel, 'A total of ' + total_users + ' users have joined the secret santa exchange so far. Use `$$join` to enter the exchange.')
    
    #allows a user to have the details of their partner restated
    elif message.content.startswith('$$partnerinfo'):
        if exchange_started and user_is_participant(message.author.id):
            userobj = get_participant_object(message.author.id)
            partnerobj = get_participant_object(userobj.partnerid)
            msg = 'Your partner is ' + user.partner + user.partnerid + '\n'
            msg = msg + 'Their mailing address is ' + partnerobj.address + '\n'
            msg = msg + 'their gift preference is as follows:\n'
            msg = msg + partnerobj.preferences
            await client.send_message(message.author, msg)
        elif exchange_started:
            await client.send_message(message.channel, '`Error: partners have not been assigned yet.`')
        else:
            await client.send_message(message.author, '`Error: You are not participating in the gift exchange.`')

@client.event
async def on_ready():
    """print message when client is connected"""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord initiation
client.run(config['programData']['discord_token'])
