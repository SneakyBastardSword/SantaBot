import logging
import asyncio
import os.path
import random
import copy
import discord
from discord.ext import commands
import CONFIG
import BOT_ERROR
import idx_list
import datetime as DT
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
        if (self.wishlisturl == "None") or (self.wishlisturl == ""):
            return False
        else:
            return True
    
    def pref_is_set(self):
        """returns whether the user has set gift preferences"""
        if (self.preferences == "None") or (self.preferences == ""):
            return False
        else:
            return True

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
    """Generate a proposed partner list"""
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
    """Make sure that everybody has a partner
    and nobody is partnered with themselves"""
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

bot = commands.Bot(command_prefix = CONFIG.prefix)

@bot.event
async def on_ready():
    """print message when client is connected"""
    currentDT = DT.datetime.now()
    print('------')
    print (currentDT.strftime("%Y-%m-%d %H:%M:%S"))
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity = discord.Game(name = CONFIG.prefix + "help"))
    print('------')

@bot.command()
async def ping(ctx):
    '''
    = Basic ping command
    '''
    latency = bot.latency
    await ctx.send("{0} milliseconds".format(round(latency, 4)*1000))

@bot.command()
async def ding(ctx):
    await ctx.send("dong")

@bot.command()
async def echo(ctx, *content:str):
    '''
    [content] = echos back the [content]
    '''
    if(len(content) == 0):
        pass
    else:
        await ctx.send(' '.join(content))

@bot.command()
async def setwishlisturl(ctx, *destination:str):
    '''
     [Any number of wishlist URLs or mailing addresses] = set wishlist destinations or mailing address. Surround mailing address with quotation marks and separate EACH wishlist destination with a space (eg. amazon.com "P. Sherman 42 Wallaby Way, Sydney" ).
    '''
    currAuthor = ctx.author
    if user_is_participant(currAuthor.id, usr_list):
        if(ctx.message.channel.is_private):
            pass
        else:
            await ctx.messsage.delete()
        (index, user) = get_participant_object(currAuthor.id, usr_list)
        new_wishlist = "None"
        if(len(destination) == 0):
            pass
        else:
            new_wishlist = ", ".join(destination)
        try:
            # save to config file
            config['members'][str(user.usrnum)][idx_list.WISHLISTURL] = new_wishlist
            config.write()
            # add the input to the value in the user's class instance
            user.wishlisturl = new_wishlist
            try:
                await currAuthor.send("New wishlist URL: {0}".format(new_wishlist))
            except:
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        except:
            try:
                await currAuthor.send(BOT_ERROR.INVALID_INPUT)
            except:
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return
    
@bot.command()
async def getwishlisturl(ctx):
    '''
     = get return current wishlist url
    '''
    currAuthor = ctx.author
    if user_is_participant(ctx.author.id, usr_list):
        (index, user) = get_participant_object(ctx.author.id, usr_list)
        try:
            await currAuthor.send("Current wishlist destination(s): {0}".format(user.wishlisturl))
        except:
            await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return

@bot.command()
async def setprefs(ctx, *preferences:str):
    currAuthor = ctx.author
    if user_is_participant(currAuthor.id, usr_list):
        if(ctx.message.channel.is_private):
            pass
        else:
            ctx.message.delete()
    return

@bot.command()
async def join(ctx):
    '''
    Join Secret Santa if it has not started. Contact the Secret Santa admin if you wish to join.
    '''
    currAuthor = ctx.author
    # check if the exchange has already started
    if user_is_participant(currAuthor.id, usr_list):
        await ctx.send(BOT_ERROR.ALREADY_JOINED)
    else:
        # initialize instance of Participant for the author
        highest_key = highest_key + 1
        usr_list.append(Participant(currAuthor.name, currAuthor.discriminator, currAuthor.id, highest_key))
        # write details of the class isntance to config and increment total_users
        config['members'][str(highest_key)] = [currAuthor.name, currAuthor.discriminator, currAuthor.id, highest_key, "", "", ""]
        config.write()

        # prompt user about inputting info
        ctx.send(currAuthor.mention + " has been added to the {0} Secret Santa exchange!".format(str(ctx.guild)) + "\nMore instructions have been DMd to you.")
        try:
            userPrompt = """Welcome to the __{0}__ Secret Santa! Please input your wishlist URL and preferences **(by DMing this bot)** so your Secret Santa can send you something.\n
                Use `s!setwishlisturl [wishlist urls separated by | ]` to set your wishlist URL (you may also add your mailing address).\n
                Use `s!setprefs [preferences separated by | ]` to set gift preferences for your Secret Santa. Put N/A if none.""".format(str(ctx.guild))
            currAuthor.send(userPrompt)
        except:
            ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    return

@bot.command()
async def invite(ctx):
    link = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=67185664".format(CONFIG.client_id)
    await ctx.send_message("Non-testing bot invite link: {0}".format(link))

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
#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='./files/debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

bot.run(CONFIG.discord_token, reconnect = True)