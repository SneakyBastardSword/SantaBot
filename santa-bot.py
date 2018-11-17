import logging
import asyncio
import os.path
import random
import copy
import discord
import CONFIG
from configobj import ConfigObj

class Participant(object):
    """class defining a participant and info associated with them"""
    def __init__(self, name, discriminator, idstr, usrnum, address='', preferences='', partnerid=''):
        self.name = name                   #string containing name of user
        self.discriminator = discriminator #string containing discriminant of user
        self.idstr = idstr                 #string containing id of user
        self.usrnum = usrnum               #int value referencing the instance's location in usr_list
        self.address = address             #string for user's address
        self.preferences = preferences     #string for user's gift preferences
        self.partnerid = partnerid         #string for id of partner
    
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
try:
    config = ConfigObj('./files/botdata.cfg', file_error = True)
except: 
    os.mkdir('./files/')
    config = ConfigObj()
    config.filename = './files/botdata.cfg'
    config['programData'] = {'exchange_started': False, 'discord_token': CONFIG.discord_token}
    config['members'] = {}
    config.write()

#initialize data from config file
server = ''
usr_list = []
highest_key = 0
exchange_started = config['programData'].as_bool('exchange_started')
for key in config['members']:
    data = config['members'][str(key)]
    usr_list.append(Participant(data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
    highest_key = int(key)

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
    for (index, person) in enumerate(usrlist):
        if person.idstr == usrid:
            return (index, person)
            break

def propose_partner_list(usrlist):
    usr_list_copy = copy.deepcopy(usrlist)
    partners = copy.deepcopy(usrlist)
    ## propose partner list
    for user in usr_list_copy:
        candidates = partners
        #candidates.remove(user)
        partner = candidates[random.randint(0, len(candidates) - 1)]
        while(partner.idstr == user.idstr):
            partner = candidates[random.randint(0, len(candidates) - 1)]
            if((len(candidates) == 1) & (candidates[0].idstr == user.idstr)):
                break # no choice but to pick yourself (this will be declared invalid later)
        #remove user's partner from list of possible partners
        partners.remove(partner)
        #save the partner id to the participant's class instance
        user.partnerid = partner.idstr
    return usr_list_copy

## everybody has a partner, nobody's partnered with themselves
def partners_are_valid(usrlist):
    if(not usrlist):
        return False
    result = True
    for user in usrlist:
        result = result & (user.partnerid != '') & (user.partnerid != user.idstr)
    return result

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
    
    global curr_server
    global usr_list
    global highest_key
    global exchange_started

    curr_server = message.server
    #write all messages to a chatlog
    if((message.content[0:1]) == "$$"):
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
        elif exchange_started:
            await client.send_message(message.channel, '`Error: Too late, the gift exchange is already in progress.`')
        else:
            #initialize instance of participant class for the author
            highest_key = highest_key + 1
            usr_list.append(Participant(message.author.name, message.author.discriminator, message.author.id, highest_key))
            #write details of the class instance to config and increment total_users
            config['members'][str(highest_key)] = [message.author.name, message.author.discriminator, message.author.id, highest_key, '', '', '']
            config.write()
            
            #prompt user about inputting info
            await client.send_message(message.channel, message.author.mention + " has been added to the {0} Secret Santa exchange!".format(str(curr_server)))
            await client.send_message(message.author, 'Please input your mailing address so your Secret Santa can send you something!\n'
            + 'Use `$$setaddress` to set your mailing adress\n'
            + 'Use `$$setprefs` to set gift preferences for your secret santa')

    elif message.content.startswith('$$leave'):
        if user_is_participant(message.author.id):
            print(usr_list)
            (index, user) = get_participant_object(message.author.id)
            #del usr_list[index]
            print(user)
            usr_list.remove(user)
            popped_user = config['members'].pop(str(user.usrnum))
            config.write()
            await client.send_message(message.channel, message.author.mention + " has left the {0} Secret Santa exchange".format(str(curr_server)))
        else:
            await client.send_message(message.channel, "You're not currently a member of the secret santa")
    
    #accept address of participants
    elif message.content.startswith('$$setaddress'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            (index, user) = get_participant_object(message.author.id)
            user.address = message.content.replace('$$setaddress ', '', 1)
            #save to config file
            config['members'][str(user.usrnum)][4] = user.address
            config.write()
            await client.delete_message(message)
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
            await client.delete_message(message)

    elif message.content.startswith('$$getaddress'):
        if user_is_participant(message.author.id):
            (index, user) = get_participant_object(message.author.id)
            await client.send_message(message.author, "Current address(es): " + str(user.address))
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #accept gift preferences of participants
    elif message.content.startswith('$$setprefs'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            (index, user) = get_participant_object(message.author.id)
            user.preferences = message.content.replace('$$setprefs ', '', 1)
            #save to config file
            config['members'][str(user.usrnum)][5] = user.preferences
            config.write()
            await client.delete_message(message)
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
            await client.delete_message(message)
    
    elif message.content.startswith('$$getprefs'):
        if user_is_participant(message.author.id):
            (index, user) = get_participant_object(message.author.id)
            await client.send_message(message.author, "Current preference(s): " + str(user.preferences))
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #command for admin to begin the secret santa partner assignmenet
    elif message.content.startswith('$$start'):
        #only allow people with admin permissions to run
        if message.author.top_role == message.server.role_hierarchy[0]:
            #first ensure all users have all info submitted
            all_fields_complete = True
            for user in usr_list:
                if user.address_is_set() and user.pref_is_set():
                    pass
                else:
                    all_fields_complete = False
                    await client.send_message(message.author, '`Error: ' + user.name + ' has not submitted either a mailing address or gift preferences.`')
                    await client.send_message(message.author, '`Partner assignment canceled: participant info incomplete.`')
            
            #select a random partner for each participant if above loop found no empty values
            if all_fields_complete:
                print("proposing a list")
                potential_list = propose_partner_list(usr_list)
                while(not partners_are_valid):
                    print("proposing a list")
                    potential_list = propose_partner_list(usr_list)
                #save to config file
                print("list passed")
                for user in potential_list:
                    (temp_index, temp_user) = get_participant_object(user.idstr)
                    (index, partner) = get_participant_object(user.partnerid, potential_list)
                    temp_user.partnerid = user.partnerid
                    config['members'][str(user.usrnum)][6] = user.partnerid # update config file
                    config.write()
                    #tell participants who their partner is
                    this_user = discord.User(name = user.name, discriminator = user.discriminator, id = user.idstr)
                    this_partner = discord.User(name = partner.name, discriminator = partner.discriminator, id = partner.idstr)
                    message_pt1 = str(partner.name) + '#' + str(partner.discriminator) + ' is your secret santa partner! Now pick out a gift for them and send it to them!'
                    message_pt2 = 'Their mailing address is: ' + partner.address
                    message_pt3 = 'Here are their gift preferences: ' + partner.preferences
                    santa_message = message_pt1 + '\n' + message_pt2 + '\n' + message_pt3
                    await client.send_message(this_user, santa_message)
                #set exchange_started + assoc. cfg value to True
                exchange_started = True
                config['programData']['exchange_started'] = True
                config.write()
                usr_list = copy.deepcopy(potential_list)
                await client.send_message(message.channel, "Secret Santa pairs have been picked! Check your PMs and remember not to let your partner know. Have fun!")
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #allows a way to exit the bot
    elif message.content.startswith('$$shutdown') and not message.channel.is_private:
        #Fonly allow ppl with admin permissions to run
        if message.author.top_role == message.server.role_hierarchy[0]:
            await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
            client.close()
            raise KeyboardInterrupt
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #lists off all participant names and id's
    elif message.content.startswith('$$listparticipants'):
        if highest_key == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        else:
            msg = '```The following people are signed up for the secret santa exchange:\n'
            for user in usr_list:
                this_user = discord.User(user = user.name, id = user.idstr)
                msg = msg + str(user.name) + '#' + str(user.discriminator) + '\n'
            msg = msg + 'Use `$$join` to enter the exchange.```'
            await client.send_message(message.channel, msg)
    
    #lists total number of participants
    elif message.content.startswith('$$totalparticipants'):
        if highest_key == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        elif highest_key == 1:
            await client.send_message(message.channel, '1 person has signed up for the secret santa exchange. Use `$$join` to enter the exchange.')
        else:
            await client.send_message(message.channel, 'A total of ' + len(usr_list) + ' users have joined the secret santa exchange so far. Use `$$join` to enter the exchange.')
    
    #allows a user to have the details of their partner restated
    elif message.content.startswith('$$partnerinfo'):
        if exchange_started and user_is_participant(message.author.id):
            (usr_index, user) = get_participant_object(message.author.id)
            (partner_index, partnerobj) = get_participant_object(user.partnerid)
            msg = 'Your partner is ' + partnerobj.name + user.partnerid + '\n'
            msg = msg + 'Their mailing address is ' + partnerobj.address + '\n'
            msg = msg + 'their gift preference is as follows:\n'
            msg = msg + partnerobj.preferences
            await client.send_message(message.author, msg)
        elif exchange_started:
            await client.send_message(message.channel, '`Error: partners have not been assigned yet.`')
        else:
            await client.send_message(message.author, '`Error: You are not participating in the gift exchange.`')

    elif message.content.startswith('$$help'):
        c_join = "`$$join` = join the Secret Santa"
        c_leave = "`$$leave` = leave the Secret Santa"
        c_setaddress = "`$$setaddress [mailing address/wishlist URL]` = set your address (replaces current)"
        c_getaddress = "`$$getaddress` = bot will PM you your current address"
        c_setprefs = "`$$setprefs [specific preferences, the things you like]` = set preferences (replaces current)"
        c_getprefs = "`$$getprefs` = bot will PM you your current preferences"
        c_listparticipants = "`$$listparticipants` = get the current participants"
        c_totalparticipants = "`$$totalparticipants` = get the total number of participants"
        c_partnerinfo = "`$$partnerinfo` = be DM'd your partner's information"
        c_start = "`$$start` **(admin only)** = assign Secret Santa partners"
        c_shutdown = "`$$shutdown` **(admin only)** = end Secret Santa"
        command_list = [c_join, c_leave, c_setaddress, c_setprefs, c_listparticipants, c_totalparticipants, c_partnerinfo, c_start, c_shutdown]
        command_string = ''
        for command in command_list:
            command_string = command_string + ("{0}\n".format(command))
        await client.send_message(message.channel, command_string)

@client.event
async def on_ready():
    """print message when client is connected"""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


#event loop and discord initiation
client.run(config['programData']['discord_token'])
