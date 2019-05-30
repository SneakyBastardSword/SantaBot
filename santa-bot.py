import logging
import asyncio
import os.path
import datetime as DT
from configobj import ConfigObj
import discord
from discord.ext import commands

from Helpers import *
import Participant
import CONFIG
import BOT_ERROR
import idx_list

#initialize config file
try:
    config = ConfigObj(CONFIG.cfg_path, file_error = True)
except: 
    os.mkdir(CONFIG.bot_folder)
    config = ConfigObj()
    config.filename = CONFIG.cfg_path
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
client_handler = logging.FileHandler(filename=CONFIG.dbg_path, encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

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
    [Any number of wishlist URLs or mailing addresses] = set wishlist destinations or mailing address. Surround mailing address with quotation marks and separate EACH wishlist destination with a space (eg. amazon.com "P. Sherman 42 Wallaby Way, Sydney" http://rightstufanime.com/).
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
            new_wishlist = " | ".join(destination)
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
    Get current wishlist
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
    '''
    Set new preferences
    '''
    currAuthor = ctx.author
    if user_is_participant(currAuthor.id, usr_list):
        if(ctx.message.channel.is_private):
            pass
        else:
            ctx.message.delete()
        (index, user) = get_participant_object(currAuthor, usr_list)
        new_prefs = "None"
        if(len(preferences) == 0):
            pass
        else:
            new_prefs = " | ".join(preferences)
        try:
            #save to config file
            config['members'][str(user.usrnum)][idx_list.PREFERENCES] = str(new_prefs)
            config.write()
            #add the input to the value in the user's class instance
            user.preferences = new_prefs
            try:
                await currAuthor.send("New preferences: {0}".format(new_prefs))
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
async def getprefs(ctx):
    '''
    Get current preferences
    '''
    currAuthor = ctx.author
    if user_is_participant(ctx.author.id, usr_list):
        (index, user) = get_participant_object(ctx.author.id, usr_list)
        try:
            await currAuthor.send("Current preference(s): {0}".format(user.preferences))
        except:
            await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return

@bot.command()
async def start(ctx):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    if(currAuthor.top_role == ctx.guild.role_hierarchy[0]):
        # first ensure all users have all info submitted
        all_fields_complete = True
        for user in usr_list:
            if(user.wishlisturl_is_set() and user.pref_is_set()):
                pass
            else:
                all_fields_complete = False
                try:
                    await currAuthor.send(BOT_ERROR.HAS_NOT_SUBMITTED(user.name))
                    await ctx.send("`Partner assignment cancelled: participant info incomplete.`")
                except:
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        
        # select a random partner for each participant if all information is complete and there are enough people to do it
        if(all_fields_complete and (len(usr_list) > 1)):
            print("Proposing a partner list")
            potential_list = propose_partner_list(usr_list)
            while(not partners_are_valid(potential_list)):
                print("Proposing a partner list")
                potential_list = propose_partner_list(usr_list)
            # save to config file
            print("Partner assignment successful")
            for user in potential_list:
                (temp_index, temp_user) = get_participant_object(user.idstr, usr_list)
                (index, partner) = get_participant_object(user.partnerid, potential_list)
                temp_user.partnerid = user.partnerid
                config['members'][str(user.usrnum)][idx_list.PARTNERID] = user.partnerid
                config.write()
                # tell participants who their partner is
                this_user = discord.User(name = user.name, discriminator = user.discriminator, id = user.idstr)
                this_user = discord.User(name = partner.name, discriminator = partner.discriminator, id = partner.idstr)
                message_pt1 = str(partner.name) + "#" + str(partner.discriminator) + " is your Secret Santa partner! Mosey on over to their wishlist URL(s) and pick out a gift! Remember to keep it in the $10-20 range.\n"
                message_pt2 = "Their wishlist(s) can be found here: " + partner.wishlisturl + "\n"
                message_pt3 = "And their gift preferences can be found here: " + partner.preferences + "\n"
                message_pt4 = "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *secret* santa, after all!"
                santa_message = message_pt1 + message_pt2 + message_pt3 + message_pt4
                try:
                    await this_user.send(santa_message)
                except:
                    await currAuthor.send("Failed to send message to {0}#{1} about their partner. Harass them to turn on server DMs for Secret Santa stuff.".format(this_user.name, this_user.discriminator))
            
            # mark the exchange as in-progress
            exchange_started = True
            is_paused = False
            config['programData']['exchange_started'] = True
            config.write()
            usr_list = copy.deepcopy(potential_list)
            await ctx.send("Secret Santa pairs have been picked! Check your PMs and remember not to let your partner know. Have fun!")
        elif not all_fields_complete:
            await ctx.send(currAuthor.mention + BOT_ERROR.SIGNUPS_INCOMPLETE)
        elif not (len(usr_list) > 1):
            await ctx.send(BOT_ERROR.NOT_ENOUGH_SIGNUPS)
        else:
            await ctx.send(BOT_ERROR.UNREACHABLE)
    else:
        await ctx.send(BOT_ERROR.NO_PERMISSION)
    return

@bot.command()
async def restart(ctx):
    # TODO: add help menu instruction
    is_paused = True
    currAuthor = ctx.author
    if((currAuthor.top_role == ctx.guild.role_hierarchy[0]) and is_paused):
        # ensure all users have all info submitted
        all_fields_complete = True
        for user in usr_list:
            if(user.wishlisturl_is_set() and user.pref_is_set()):
                pass
            else:
                all_fields_complete = False
                try:
                    await currAuthor.send(BOT_ERROR.HAS_NOT_SUBMITTED(user.name))
                    await ctx.send("`Partner assignment cancelled: participant info incomplete.`")
                except:
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        list_changed = usr_list_changed_during_pause(usr_list, user_left_during_pause)
        if(list_changed):
            ctx.send("User list changed during the pause. Partners must be picked again with `{0}start`.".format(CONFIG.prefix))
        else:
            exchange_started = True
            is_paused = False
            config['programData']['exchange_started'] = True
            config.write()
            await ctx.send("No change was made during the pause. Secret Santa resumed with the same partners.")
    elif(currAuthor.top_role != ctx.guild.role_hierarchy[0]):
        await ctx.send(BOT_ERROR.NO_PERMISSION)
    elif(not is_paused):
        await ctx.send(BOT_ERROR.NOT_PAUSED)
    else:
        await ctx.send(BOT_ERROR.UNREACHABLE)
    return

@bot.command()
async def pause(ctx):
    # TODO: add help menu instruction
    if(ctx.author.top_role == ctx.guild.role_hierarchy[0]):
        exchange_started = False
        config['programData']['exchange_started'] = False
        config.write()
        is_paused = True
        await ctx.send("Secret Santa has been paused. New people may now join.")
    else:
        await ctx.send(BOT_ERROR.NO_PERMISSION)
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
                Use `{1}setwishlisturl [wishlist urls separated by | ]` to set your wishlist URL (you may also add your mailing address).\n
                Use `{2}setprefs [preferences separated by | ]` to set gift preferences for your Secret Santa. Put N/A if none.""".format(str(ctx.guild), CONFIG.prefix, CONFIG.prefix)
            currAuthor.send(userPrompt)
        except:
            ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    return

@bot.command()
async def end(ctx):
    # TODO: add help menu instruction
    if(ctx.author.top_role == ctx.guild.role_hierarchy[0]):
        exchange_started = False
        is_paused = False
        config['programData']['exchange_started'] = False
        highest_key = 0
        del usr_list[:]
        print(len(usr_list))
        config['members'].clear()
        config.write()
        await ctx.send("Secret Santa ended")
    else:
        ctx.send(BOT_ERROR.NO_PERMISSION)
    return

@bot.command()
async def listparticipants(ctx):
    # TODO: add help menu instruction
    if(ctx.author.top_role == ctx.guild.role_hierarchy[0]):
        if(highest_key == 0):
            await ctx.send("Nobody has signed up for the secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
        else:
            msg = '```The following people are signed up for the Secret Santa exchange:\n'
            for user in usr_list:
                this_user = discord.User(user = user.name, id = user.idstr)
                msg = msg + str(user.name) + "#" + str(user.discriminator) + "\n"
            msg = msg + "\nUse `{0}join` to enter the exchange.```".format(CONFIG.prefix)
    else:
        ctx.send(BOT_ERROR.NO_PERMISSION)
    return

@bot.command()
async def totalparticipants(ctx):
    # TODO: add help menu instruction
    if highest_key == 0:
        await ctx.send("Nobody has signed up for the Secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
    elif highest_key == 1:
        await ctx.send("1 person has signed up for the Secret Santa exchange. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
    else:
        await ctx.send("{0} people have joined the Secret Santa exchange so far. Use `{1}join` to enter the exchange.".format(str(len(usr_list)), CONFIG.prefix))
    return

@bot.command()
async def partnerinfo(ctx):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    authorIsParticipant = user_is_participant(currAuthor.id, usr_list)
    if(exchange_started and authorIsParticipant):
        (usr_index, user) = get_participant_object(currAuthor, usr_list)
        (partner_index, partnerobj) = get_participant_object(user.partnerid, usr_list)
        msg = "Your partner is " + partnerobj.name + "#" + partnerobj.discriminator + "\n"
        msg = msg + "Their wishlist(s) can be found here: " + partnerobj.wishlisturl + "\n"
        msg = msg + "And their gift preferences can be found here: " + partnerobj.preferences + "\n"
        msg = msg + "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *Secret* Santa, after all!"
        try:
            await currAuthor.send(msg)
            await ctx.send("The information has been sent to your DMs.")
        except:
            await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    elif((not exchange_started) and authorIsParticipant):
        await ctx.send(BOT_ERROR.NOT_STARTED)
    elif(exchange_started and (not authorIsParticipant)):
        await ctx.send(BOT_ERROR.EXCHANGE_STARTED_UNJOINED)
    elif((not exchange_started) and (not authorIsParticipant)):
        await ctx.send(BOT_ERROR.UNJOINED)
    else:
        await ctx.send(BOT_ERROR.UNREACHABLE)
    return

@bot.command()
async def invite(ctx):
    link = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=67185664".format(CONFIG.client_id)
    await ctx.send_message("Bot invite link: {0}".format(link))

bot.run(CONFIG.discord_token, reconnect = True)