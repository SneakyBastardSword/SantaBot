import logging
import os.path
import discord
from random import randint
from configobj import ConfigObj


class Group(object):
    """class defining a group of participants based on server membership"""
    def __init__(self, name, idstr, totalUsers=0, participantList=[], hasStarted=False):
        self.name = name                #server name
        self.idstr = idstr              #server ID
        self.totalUsers = totalUsers
        self.participantList = participantList  #participant list, populated as users join
        self.hasStarted = hasStarted

    class Participant(object):
        """contains info for individual users"""
        def __init__(self, name, idstr, usrnum, partnerid='', address='', prefs=''):
            self.name = name
            self.idstr = idstr
            self.usrnum = usrnum
            self.partnerid = partnerid
            self.address = address
            self.prefs = prefs

        def address_is_set(self):
            """Checks if user's address has been set"""
            if self.address == '':
                return False
            else:
                return True

        def pref_is_set(self):
            """Checks if the user's gift prefs have been set"""
            if self.prefs == '':
                return False
            else:
                return True

    def add_participant(self, name, usrid, partnerid='', address='', prefs='', saveinfo=True):
        """appends a Participant object to this group's userlist"""
        global usr_list
        newUser = self.Participant(name, usrid, self.totalUsers, partnerid, address, prefs)
        self.participantList.append(newUser)
        usr_list.append(newUser)
        self.totalUsers = self.totalUsers + 1
        if saveinfo:
            cfgEntry = config['servers'][self.idstr]
            cfgEntry['member_list'][newUser.idstr] = [name, newUser.usrnum, '', '', '']
            cfgEntry['total_users'] = self.totalUsers
            config.write()

    async def asssign_partners(self, message):
        """method to assign each user a partner"""
        partners = self.participantList
        for user in self.participantList:
            candidates = partners
            candidates.remove(user.usrnum)
            partner = candidates[randint(0, len(candidates) - 1)]
            partners.remove(partner.usrnum)
            user.partnerid = partner.idstr
            #save to config file
            config['servers'][self.idstr]['member_list'][user.usrnum].partnerid = partner.idstr
            config.write()
            #inform users of their partner
        for person in message.server.members:
            if user_is_participant(person.id):
                await client.send_message(
                    person,
                    'Your partner is ' + partner.name + '\n'
                    + 'Their address is ' + partner.address + '\n'
                    + 'Their gift preferences are as follows:\n'
                    + partner.prefs)
        #set hasStarted + assoc. cfg value to True
        self.hasStarted = True
        config['servers'][self.idstr]['has_started'] = True

client = discord.Client()
usr_list = []
svr_list = []

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

def get_group_object(serverid, serverlist=svr_list):
    """takes discord server id string and list of server objects,
    and returns first server object with matching id"""
    for group in serverlist:
        if group.idstr == serverid:
            return group

print('Loading...')

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='./files/debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

#initiate config file
if os.path.exists('./files/') and os.path.isfile('./files/botdata.cfg'):
    config = ConfigObj('./files/botdata.cfg')
    firstrun = False
else:
    if not os.path.exists('./files'):
        os.mkdir('./files')
    config = ConfigObj('./files/botdata.cfg')
    config['token'] = 'MjMzMjYyNzY4NjUwODQ2MjA4.Cxdlxw.niB4GCO-ELkHvAitUZ7zQST7QQk'
    config['servers'] = {}
    config.write()
    firstrun = True

@client.event
async def on_ready():
    """print message when client is connected and perform
    initialization of svr_list"""
    global usr_list
    global svr_list
    global firstrun

    if firstrun:
        for server in client.servers:
            svr_list.append(Group(server.name, server.id))
            config['servers'][server.id] = {
                'name': server.name,
                'has_started': False,
                'member_list': {}
                }
            config.write()
    else:
        for server in client.servers:
            svr_list.append(Group(
                server.name,
                server.id,
                0,
                [],
                config['servers'][server.id].as_bool('has_started')
            ))
            for key in config['servers'][server.id]['member_list']:
                infolist = config['servers'][server.id]['member_list'].as_list(key)
                svr_list[-1].add_participant(
                    infolist[0],
                    key,
                    infolist[1],
                    infolist[2],
                    infolist[3],
                    False)

    print('initialized server data')
    print('Logged in as')
    print(client.user.name)
    print('#' + client.user.discriminator)
    print('------')

@client.event
async def on_message(message):
    """on_event handler for all on_message events"""

    #declare global vars
    global usr_list

    #fetch author's participant class instance for convenience sake
    if user_is_participant(message.author.id):
        author = get_participant_object(message.author.id)

    #write all messages to a chatlog
    if message.channel.is_private:
        with open('./files/chat.log', 'a+') as chat_log:
            chat_log.write(
                '[Private msg from ' + message.author.name + ' at '
                + str(message.timestamp) + ']'
                + message.content + '\n')
    else:
        with open('./files/chat.log', 'a+') as chat_log:
            chat_log.write(
                '[' + message.author.name + ' in '
                + message.channel.name + ' at '
                + str(message.timestamp) + ']'
                + message.content + '\n')

    if message.author == client.user:
        return

    #create group class instance
    if message.channel.is_private:
        for server in svr_list:
            for person in server.participantList:
                if person.idstr == author.idstr:
                    group = get_group_object(server.idstr)
                    break
            if group in locals():
                break
    else:
        group = get_group_object(message.server.id)

    #event for a user joining the secret santa
    if message.content.startswith('$$join'):
        #cant really have a gift exchange in a pm
        if message.channel.is_private:
            await client.send_message(message.channel,
                                      '`Error: You must join a gift exchange through a server.`')
        #check if message author has already joined
        elif user_is_participant(message.author.id, group.participantList):
            await client.send_message(message.channel,
                                      '`Error: You have already joined this exchange.`')
        #check if the exchange has already started
        elif group.hasStarted:
            await client.send_message(
                message.channel,
                '`Error: Too late, the gift exchange is already in progress.`')
        else:
            #initialize instance of participant class for the author
            group.add_participant(message.author.name, message.author.id)
            #prompt user about inputting info
            await client.send_message(
                message.channel,
                message.author.mention
                + ' Has been added to the OfficialFam Secret Santa exchange!')
            await client.send_message(
                message.author,
                'Please input your mailing address so your secret Santa can send you something!\n'
                + 'Use `$$setaddress` to set your mailing adress\n'
                + 'Use `$$setpreference` to set gift preferences for your secret santa')

    #accept address of participants
    elif message.content.startswith('$$setaddress'):
        print('foobar')
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            author.address = message.content.replace('$$setaddress', '', 1)
            await client.send_message(message.author, 'Address saved.')
            #save to config file
            config['servers'][group.idstr]['member_list'][author.idstr][2] = author.address
            config.write()
        else:
            await client.send_message(
                message.channel,
                'Error: you have not yet joined the secret santa exchange. '
                + 'Use `$$join` to join the exchange.')

    #accept gift preferences of participants
    elif message.content.startswith('$$setprefs'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            author.preferences = message.content.replace('$$setpref', '', 1)
            await client.send_message(message.author, 'Gift preferences saved.')
            #save to config file
            config['servers'][group.idstr]['member_list'][author.idstr][3] = author.prefs
            config.write()
        else:
            await client.send_message(
                message.channel,
                'Error: you have not yet joined the secret santa exchange. '
                + 'Use `$$join` to join the exchange.')

    #command for admin to begin the secret santa partner assignmenet
    elif message.content.startswith('$$start'):
        #only allow people with admin permissions to run
        if message.author.top_role == message.server.role_heirarchy[0]:
            #first ensure all users have all info submitted
            all_fields_complete = True
            for user in usr_list:
                if user.address_is_set() and user.pref_is_set():
                    pass
                else:
                    all_fields_complete = False
                    await client.send_message(
                        message.author,
                        '`Error: ' + user.name
                        + ' has not submitted either a mailing address or gift preferences.`')
                    await client.send_message(
                        message.author,
                        '`Partner assignment canceled: participant info incomplete.`')
                    break
            #select a random partner for each participant if above loop found no empty values
            if all_fields_complete:
                group.asssign_partners()
        else:
            await client.send_message(
                message.channel,
                '`Error: you do not have permission to do this.`')

    #allows a way to exit the bot
    elif message.content.startswith('$$shutdown') and not message.channel.is_private:
        #Fonly allow ppl with admin permissions to run
        if message.author.top_role == message.server.role_heirarchy[0]:
            await client.send_message(message.channel, 'Curse your sudden but inevitable betrayal!')
            raise KeyboardInterrupt
        else:
            await client.send_message(
                message.channel,
                '`Error: you do not have permission to do this.`')

    #lists off all participant names and id's
    elif message.content.startswith('$$listparticipants'):
        if group.totalUsers == 0:
            await client.send_message(
                message.channel,
                '`Nobody has signed up for the secret santa exchange yet. '
                + 'Use "$$join" to enter the exchange.`')
        else:
            msg = '```The following people are signed up for the secret santa exchange:\n'
            for user in group.participantList:
                msg = msg + user.name + '\n'
            msg = msg + 'Use "$$join" to enter the exchange.```'
            await client.send_message(message.channel, msg)

    #lists total number of participants
    elif message.content.startswith('$$totalparticipants'):
        if group.totalUsers == 0:
            await client.send_message(
                message.channel,
                '`Nobody has signed up for the secret santa exchange yet. '
                + 'Use "$$join" to enter the exchange.`')
        elif group.totalUsers == 1:
            await client.send_message(
                message.channel,
                '`1 person has signed up for the secret santa exchange. '
                + 'Use "$$join" to enter the exchange.`')
        else:
            await client.send_message(
                message.channel,
                '`A total of ' + group.totalUsers
                + ' users have joined the secret santa exchange so far. '
                + 'Use "$$join" to enter the exchange.`')

    #allows a user to have the details of their partner restated
    elif message.content.startswith('$$partnerinfo'):
        if group.hasStarted and user_is_participant(message.author.id):
            partnerobj = get_participant_object(author.partnerid)
            msg = 'Your partner is ' + partnerobj.name + '\n'
            msg = msg + 'Their mailing address is ' + partnerobj.address + '\n'
            msg = msg + 'their gift preference is as follows:\n'
            msg = msg + partnerobj.preferences
            await client.send_message(message.author, msg)
        elif not group.hasStarted:
            await client.send_message(
                message.channel,
                '`Error: partners have not been assigned yet.`')
        else:
            await client.send_message(
                message.author,
                '`Error: You are not participating in the gift exchange.`')

    elif message.content.startswith('$$help'):
        await client.send_message(
            message.channel,
            'SantaBot Help Message\nGeneral user commands:'
            + '`$$join`- Join the current server\'s gift exchange'
            + '`$$listparticipants`- List people participating in the current server\'s exchange'
            + '`$$totalparticipants`- '
            + 'Return the total number of people in the current server\'s exchange')


#event loop and discord initiation
try:
    client.run(config['token'])
except discord.LoginFailure:
    print(
        'Error: The token in /files/botdata.cfg is invalid.\n'
        + 'If this is the first time running the bot from this directory, then this is normal.\n'
        + 'To fix, change the contents of the first line of /files/botdata.cfg after the "="\n'
        + 'to a valid discord bot token.')
