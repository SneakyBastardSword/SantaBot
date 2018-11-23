import logging
import asyncio
import os.path
import random
import copy
import discord
import CONFIG
import BOT_ERROR
import idx_list
from configobj import ConfigObj

class Participant(object):
    """class defining a participant and info associated with them"""
    def __init__(self, name, discriminator, idstr, usrnum, wishlisturl='', preferences='', partnerid=''):
        self.name = name                   #string containing name of user
        self.discriminator = discriminator #string containing discriminant of user
        self.idstr = idstr                 #string containing id of user
        self.usrnum = usrnum               #int value referencing the instance's location in usr_list
        self.wishlisturl = wishlisturl             #string for user's wishlisturl
        self.preferences = preferences     #string for user's gift preferences
        self.partnerid = partnerid         #string for id of partner
    
    def wishlisturl_is_set(self):
        """returns whether the user has set an wishlisturl"""
        if self.wishlisturl == '':
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
    config['programData'] = {'exchange_started': False}
    config['members'] = {}
    config.write()

#initialize data from config file
server = ''
usr_list = []
highest_key = 0
user_left_during_pause = False
is_paused = False
exchange_started = config['programData'].as_bool('exchange_started')
for key in config['members']:
    data = config['members'][str(key)]
    usr = Participant(data[idx_list.NAME], data[idx_list.DISCRIMINATOR], data[idx_list.IDSTR], data[idx_list.USRNUM], data[idx_list.WISHLISTURL], data[idx_list.PREFERENCES], data[idx_list.PARTNERID])
    usr_list.append(usr)
    highest_key = int(key)

def user_is_participant(usrid, usrlist):
    """Takes a discord user ID string and returns whether
    a user with that ID is in usr_list"""
    result = False
    for person in usrlist:
        if person.idstr == usrid:
            result = True
            break
    return result

def get_participant_object(usrid, usrlist):
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

## checks if the user list changed during a pause
def usr_list_changed_during_pause(usrlist, usr_left):
    if(usr_left):# there's probably a better boolean logic way but this is easy
        usr_left = False # acknowledge
        return True

    has_changed = True
    for user in usrlist:
        has_match = (not (str(user.partnerid) == ""))
        has_changed = has_changed & has_match # figures out if all users have a match
    has_changed = has_changed & (not usr_left)
    return (not has_changed) ## if not all users have a match

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
    global user_left_during_pause
    global is_paused

    message_split = message.content.split()
    curr_server = message.server
    #write all messages to a chatlog
    if((message.content[0:2]) == "s!"):
        print(message.content)
        with open('./files/chat.log', 'a+') as chat_log:
            chat_log.write("[{0}#{1} ({2}) at {3}] {4}\n".format(message.author.name, message.author.discriminator, message.author.id, str(message.timestamp), message.content))
            pass
    
        #ignore messages from the bot itself
        if message.author == client.user:
            return
        
        #event for a user joining the Secret Santa
        elif(message_split[0] == "s!join"):
            #check if message author has already joined
            if user_is_participant(message.author.id, usr_list):
                await client.send_message(message.channel, '`Error: You have already joined.`')
            #check if the exchange has already started
            elif exchange_started:
                await client.send_message(message.channel, BOT_ERROR.EXCHANGE_IN_PROGRESS)
            else:
                #initialize instance of participant class for the author
                highest_key = highest_key + 1
                usr_list.append(Participant(message.author.name, message.author.discriminator, message.author.id, highest_key))
                #write details of the class instance to config and increment total_users
                config['members'][str(highest_key)] = [message.author.name, message.author.discriminator, message.author.id, highest_key, '', '', '']
                config.write()
                
                #prompt user about inputting info
                await client.send_message(message.channel, message.author.mention + " has been added to the {0} Secret Santa exchange!".format(str(curr_server)) + "\nMore instructions have been DMd to you.")
                try:
                    await client.send_message(message.author, 'Welcome to the __' + str(curr_server) + '__ Secret Santa! Please input your wishlist URL and preferences **(by DMing this bot)** so your Secret Santa can send you something.\n'
                    + 'Use `s!setwishlisturl [wishlist urls separated by | ]` to set your wishlist URL (you may also add your mailing address).\n'
                    + 'Use `s!setprefs [preferences separated by | ]` to set gift preferences for your Secret Santa. Put N/A if none.')
                except:
                    await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)

        #event for a user to leave the Secret Santa list
        elif(message_split[0] == "s!leave"):
            if user_is_participant(message.author.id, usr_list):
                (index, user) = get_participant_object(message.author.id, usr_list)
                usr_list.remove(user)
                popped_user = config['members'].pop(str(user.usrnum))
                config.write()
                if(is_paused):
                    user_left_during_pause = True
                await client.send_message(message.channel, message.author.mention + " has left the {0} Secret Santa exchange".format(str(curr_server)))
            else:
                await client.send_message(message.channel, BOT_ERROR.UNJOINED)
        
        #accept wishlisturl of participants
        elif(message_split[0] == "s!setwishlisturl"):
            #check if author has joined the exchange yet
            if user_is_participant(message.author.id, usr_list):
                if(message.channel.is_private):
                    pass
                else:
                    await client.delete_message(message)
                (index, user) = get_participant_object(message.author.id, usr_list)
                new_wishlist = ""
                if(message.content == "s!setwishlisturl"):
                    new_wishlist = ""
                else:
                    new_wishlist = message.content.replace("s!setwishlisturl ", "", 1)
                try:
                    #save to config file
                    config['members'][str(user.usrnum)][idx_list.WISHLISTURL] = new_wishlist
                    config.write()
                    #add the input to the value in the user's class instance
                    user.wishlisturl = new_wishlist
                    try:
                        await client.send_message(message.author, "New wishlist URL: {0}".format(new_wishlist))
                    except:
                        await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
                except:
                    try:
                        await client.send_message(message.author, BOT_ERROR.INVALID_INPUT)
                    except:
                        await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
            else:
                await client.send_message(message.channel, )
        
        # get current wishlist URL(s)
        elif(message_split[0] == "s!getwishlisturl"):
            if user_is_participant(message.author.id, usr_list):
                (index, user) = get_participant_object(message.author.id, usr_list)
                try:
                    await client.send_message(message.author, "Current wishlist URL(s): {0}".format(user.wishlisturl))
                except:
                    await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
            else:
                await client.send_message(message.channel, BOT_ERROR.UNJOINED)
        
        #accept gift preferences of participants
        elif(message_split[0] == "s!setprefs"):
            #check if author has joined the exchange yet
            if user_is_participant(message.author.id, usr_list):
                if(message.channel.is_private):
                    pass
                else:
                    await client.delete_message(message)
                (index, user) = get_participant_object(message.author.id, usr_list)
                new_prefs = ""
                if(message.content == "s!setprefs"):
                    new_prefs = ""
                else:
                    new_prefs = message.content.replace("s!setprefs ", "", 1)
                try:
                    #save to config file
                    config['members'][str(user.usrnum)][idx_list.PREFERENCES] = str(new_prefs)
                    config.write()
                    #add the input to the value in the user's class instance
                    user.preferences = new_prefs
                    try:
                        await client.send_message(message.author, "New preferences: {0}".format(new_prefs))
                    except:
                        await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
                except:
                    try:
                        await client.send_message(message.author, BOT_ERROR.INVALID_INPUT)
                    except:
                        await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
            else:
                await client.send_message(message.channel, BOT_ERROR.UNJOINED)
                await client.delete_message(message)
        
        #get current preferences
        elif(message_split[0] == "s!getprefs"):
            if user_is_participant(message.author.id, usr_list):
                (index, user) = get_participant_object(message.author.id, usr_list)
                try:
                    await client.send_message(message.author, "Current preference(s): {0}".format(user.preferences))
                except:
                    await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
            else:
                await client.send_message(message.channel, BOT_ERROR.UNJOINED)
        
        #command for admin to begin the Secret Santa partner assignment
        elif(message_split[0] == "s!start"):
            #only allow people with admin permissions to run
            if message.author.top_role == message.server.role_hierarchy[0]:
                #first ensure all users have all info submitted
                all_fields_complete = True
                for user in usr_list:
                    if user.wishlisturl_is_set() and user.pref_is_set():
                        pass
                    else:
                        all_fields_complete = False
                        try:
                            await client.send_message(message.author, '`Error: ' + user.name + ' has not submitted either a mailing wishlist URL or gift preferences.`')
                            await client.send_message(message.author, '`Partner assignment canceled: participant info incomplete.`')
                        except:
                            await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
                
                #select a random partner for each participant if above loop found no empty values and there are enough people to do it
                if all_fields_complete & (len(usr_list) > 1):
                    print("proposing a list")
                    potential_list = propose_partner_list(usr_list)
                    while(not partners_are_valid(potential_list)):
                        print("proposing a list")
                        potential_list = propose_partner_list(usr_list)
                    #save to config file
                    print("list passed")
                    for user in potential_list:
                        (temp_index, temp_user) = get_participant_object(user.idstr, usr_list)
                        (index, partner) = get_participant_object(user.partnerid, potential_list)
                        temp_user.partnerid = user.partnerid
                        config['members'][str(user.usrnum)][idx_list.PARTNERID] = user.partnerid # update config file
                        config.write()
                        #tell participants who their partner is
                        this_user = discord.User(name = user.name, discriminator = user.discriminator, id = user.idstr)
                        this_partner = discord.User(name = partner.name, discriminator = partner.discriminator, id = partner.idstr)
                        message_pt1 = str(partner.name) + '#' + str(partner.discriminator) + ' is your Secret Santa partner! Mosey on over to their wishlist URL(s) and pick out a gift! Remember to keep it in the $10-20 range.\n'
                        message_pt2 = 'Their wishlist(s) can be found here: ' + partner.wishlisturl + '\n'
                        message_pt3 = 'And their gift preferences can be found here: ' + partner.preferences + '\n'
                        message_pt4 = "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *secret* santa, after all!"
                        santa_message = message_pt1 + message_pt2 + message_pt3 + message_pt4
                        try:
                            await client.send_message(this_user, santa_message)
                        except:
                            await client.send_message(message.author, "Failed to send message to {0}#{1} about their partner. Harass them to turn on server DMs for Secret Santa stuff.".format(this_user.name, this_user.discriminator))
                    #set exchange_started + assoc. cfg value to True
                    exchange_started = True
                    is_paused = False
                    config['programData']['exchange_started'] = True
                    config.write()
                    usr_list = copy.deepcopy(potential_list)
                    await client.send_message(message.channel, "Secret Santa pairs have been picked! Check your PMs and remember not to let your partner know. Have fun!")
                elif not all_fields_complete:
                    await client.send_message(message.channel, message.author.mention + " `Error: Signups incomplete. Time for some love through harassment.`")
            else:
                await client.send_message(message.channel, BOT_ERROR.NO_PERMISSION)
        
        #command allows you to restart without rematching if no change was made while s!paused
        elif(message_split[0] == "s!restart"):
            is_paused = True
            if (message.author.top_role == message.server.role_hierarchy[0]) and is_paused:
                #first ensure all users have all info submitted
                all_fields_complete = True
                for user in usr_list:
                    if user.wishlisturl_is_set() and user.pref_is_set():
                        pass
                    else:
                        all_fields_complete = False
                        try:
                            await client.send_message(message.author, '`Error: ' + user.name + ' has not submitted either a mailing wishlist URL or gift preferences.`')
                            await client.send_message(message.author, '`Partner assignment canceled: participant info incomplete.`')
                        except:
                            await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
                list_changed = usr_list_changed_during_pause(usr_list, user_left_during_pause)
                if(list_changed):
                    await client.send_message(message.channel, "User list changed during the pause. Partners must be picked again with `s!start`.")
                else:
                    exchange_started = True
                    is_paused = False
                    config['programData']['exchange_started'] = True
                    config.write()
                    await client.send_message(message.channel, "No change was made during the pause. Secret Santa resumed with the same partners.")
            elif(message.author.top_role != message.server.role_hierarchy[0]):
                await client.send_message(message.channel, BOT_ERROR.NO_PERMISSION)
            elif(not is_paused):
                await client.send_message(message.channel, "`Error: Secret Santa is not paused`")
            else:
                await client.send_message(message.channel, "idklol")

        # allows a way to restart the Secret Santa
        elif(message_split[0] == "s!pause"):
            #only allow ppl with admin permissions to run
            if (message.author.top_role == message.server.role_hierarchy[0]):
                exchange_started = False
                config['programData']['exchange_started'] = False
                config.write()
                is_paused = True
                await client.send_message(message.channel, 'Secret Santa has been paused. New people may now join.')
            else:
                await client.send_message(message.channel, BOT_ERROR.NO_PERMISSION)

        #allows a way to end the Secret Santa
        elif(message_split[0] == "s!end") and not message.channel.is_private:
            #only allow ppl with admin permissions to run
            if (message.author.top_role == message.server.role_hierarchy[0]):
                exchange_started = False
                is_paused = False
                config['programData']['exchange_started'] = False
                highest_key = 0
                del usr_list[:]
                print(len(usr_list))
                config['members'].clear()
                config.write()
                await client.send_message(message.channel, "Secret Santa ended")
            else:
                await client.send_message(message.channel, BOT_ERROR.NO_PERMISSION)
        
        #lists off all participant names and id's
        elif(message_split[0] == "s!listparticipants"):
            if (message.author.top_role == message.server.role_hierarchy[0]):
                if highest_key == 0:
                    await client.send_message(message.channel, 'Nobody has signed up for the Secret Santa exchange yet. Use `s!join` to enter the exchange.')
                else:
                    msg = '```The following people are signed up for the Secret Santa exchange:\n'
                    for user in usr_list:
                        this_user = discord.User(user = user.name, id = user.idstr)
                        msg = msg + str(user.name) + '#' + str(user.discriminator) + '\n'
                    msg = msg + 'Use `s!join` to enter the exchange.```'
                    await client.send_message(message.channel, msg)
            else:
                await client.send_message(message.channel, BOT_ERROR.NO_PERMISSION)
        
        #lists total number of participants
        elif(message_split[0] == "s!totalparticipants"):
            if highest_key == 0:
                await client.send_message(message.channel, 'Nobody has signed up for the Secret Santa exchange yet. Use `s!join` to enter the exchange.')
            elif highest_key == 1:
                await client.send_message(message.channel, '1 person has signed up for the Secret Santa exchange. Use `s!join` to enter the exchange.')
            else:
                await client.send_message(message.channel, 'A total of ' + str(len(usr_list)) + ' users have joined the Secret Santa exchange so far. Use `s!join` to enter the exchange.')
        
        #allows a user to have the details of their partner restated
        elif(message_split[0] == "s!partnerinfo"):
            if exchange_started and user_is_participant(message.author.id, usr_list):
                (usr_index, user) = get_participant_object(message.author.id, usr_list)
                (partner_index, partnerobj) = get_participant_object(user.partnerid, usr_list)
                msg = 'Your partner is ' + partnerobj.name + "#" + partnerobj.discriminator + '\n'
                msg = msg + 'Their wishlist(s) can be found here: ' + partnerobj.wishlisturl + '\n'
                msg = msg + 'And their gift preferences can be found here: ' + partnerobj.preferences + '\n'
                msg = msg + "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *secret* santa, after all!"
                try:
                    await client.send_message(message.author, msg)
                except:
                    await client.send_message(message.channel, message.author.mention + BOT_ERROR.DM_FAILED)
                await client.send_message(message.channel, "The information has been sent to your DMs.")
            elif not exchange_started:
                await client.send_message(message.channel, BOT_ERROR.NOT_STARTED)
            elif not user_is_participant(message.author.id, usr_list):
                await client.send_message(message.channel, '`Error: You are not participating in the gift exchange.`')
            else:
                await client.send_message(message.channel, "`Error: this shouldn't happen`")

        elif(message_split[0] == "s!help"):
            c_join = "`s!join` = join the Secret Santa"
            c_leave = "`s!leave` = leave the Secret Santa"
            c_setwishlisturl = "`s!setwishlisturl [wishlist urls separated by | ]` = set your wishlist URL (replaces current). You may also add your mailing address. __This field required__."
            c_getwishlisturl = "`s!getwishlisturl` = bot will PM you your current wishlist"
            c_setprefs = "`s!setprefs [preferences separated by | ]` = set preferences (replaces current). Put N/A if none. __This field required__."
            c_getprefs = "`s!getprefs` = bot will PM you your current preferences"
            c_listparticipants = "`s!listparticipants` **(admin only)** = get the current participants"
            c_totalparticipants = "`s!totalparticipants` = get the total number of participants"
            c_partnerinfo = "`s!partnerinfo` = be DMd your partner's information"
            c_start = "`s!start` **(admin only)** = assign Secret Santa partners"
            c_restart = "`s!restart` **(admin only)** = attempt to restart Secret Santa after pause without changing partners"
            c_pause = "`s!pause` **(admin only)** = pause Secret Santa (will require `s!start` and will reshuffle partners)"
            c_end = "`s!end` **(admin only)** = end Secret Santa"
            c_ping = "`s!ping` = check if bot is alive"
            command_list = [c_join, c_leave, c_setwishlisturl, c_getwishlisturl, c_setprefs, c_getprefs, c_listparticipants, c_totalparticipants, c_partnerinfo, c_start, c_pause, c_restart, c_end, c_ping]
            command_string = ''
            for command in command_list:
                command_string = command_string + ("{0}\n".format(command))
            await client.send_message(message.channel, command_string)

        elif(message_split[0] == "s!ping"):
            """ Pong! """
            await client.send_message(message.channel, "Pong!")

        elif(message_split[0] == "s!invite"):
            link = "https://discordapp.com/oauth2/authorize?client_id=513141948383756289&scope=bot&permissions=67185664"
            await client.send_message(message.channel, "Non-testing bot invite link: {0}".format(link))

        else:
            await client.send_message(message.channel, "Command not found. Please use `s!help` if you need help with the commands.")

@client.event
async def on_ready():
    """print message when client is connected"""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(game = discord.Game(name = "s!help"))
    print('------')


#event loop and discord initiation
client.run(CONFIG.discord_token)