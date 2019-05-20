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

bot = commands.Bot(command_prefix = CONFIG.prefix)

@bot.event
async def on_ready():
    """print message when client is connected"""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    game = discord.Game(name = "s!help")
    await bot.change_presence(activity = game)
    print('------')

@bot.command()
async def ping(ctx):
    '''
    = Basic ping command
    '''
    await ctx.send("pong")

@bot.command()
async def echo(ctx, content:str, number:int = 1, *args):
    '''
    [content]
    '''
    for x in range(number):
        await ctx.send(content)
    await ctx.send("{1}".format(len(args)))

@bot.command()
async def setwishlisturl(ctx, urls:str):
    await ctx.send(urls)
    return

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

bot.run(CONFIG.discord_token, reconnect = True)