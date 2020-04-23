import asyncio
import datetime as DT
import logging
import os
import copy

import discord
from configobj import ConfigObj
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument

import BOT_ERROR
import CONFIG
from SantaBotConstants import SantaBotConstants
from SantaBotHelpers import SantaBotHelpers
from Participant import Participant

#initialize config file
try:
    config = ConfigObj(CONFIG.cfg_path, file_error = True)
except: 
    try:
        os.mkdir(CONFIG.bot_folder)
    except:
        pass
    config = ConfigObj()
    config.filename = CONFIG.cfg_path
    config['programData'] = {'exchange_started': False}
    config['members'] = {}
    config.write()
#initialize data from config file
global usr_list
global highest_key
global exchange_started
global user_left_during_pause
global is_paused

server = ''
usr_list = []
highest_key = 0
user_left_during_pause = False
is_paused = False
SantaBotHelper = SantaBotHelpers()

exchange_started = config['programData'].as_bool('exchange_started')
for key in config['members']:
    data = config['members'][str(key)]
    usr = Participant(data[SantaBotConstants.NAME], data[SantaBotConstants.DISCRIMINATOR], data[SantaBotConstants.IDSTR], data[SantaBotConstants.USRNUM], data[SantaBotConstants.WISHLISTURL], data[SantaBotConstants.PREFERENCES], data[SantaBotConstants.PARTNERID])
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
async def ping(ctx: commands.Context):
    '''
    = Basic ping command
    '''
    latency = bot.latency
    await ctx.send("{0} milliseconds".format(round(latency, 4)*1000))

@bot.command()
async def ding(ctx: commands.Context):
    await ctx.send("dong")

@bot.command()
async def echo(ctx: commands.Context, *content:str):
    '''
    [content] = echos back the [content]
    '''
    if(len(content) == 0):
        pass
    else:
        await ctx.send(' '.join(content))

@bot.command()
async def setwishlisturl(ctx: commands.Context, *destination:str):
    '''
    [Any number of wishlist URLs or mailing addresses] = set wishlist destinations or mailing address. Surround mailing address with quotation marks and separate EACH wishlist destination with a space (eg. amazon.com "P. Sherman 42 Wallaby Way, Sydney" http://rightstufanime.com/).
    '''
    currAuthor = ctx.author
    global usr_list
    if SantaBotHelper.user_is_participant(currAuthor.id, usr_list):
        if(SantaBotHelper.channelIsPrivate(ctx.channel)):
            pass
        else:
            await ctx.message.delete()
        (index, user) = SantaBotHelper.get_participant_object(currAuthor.id, usr_list)
        new_wishlist = "None"
        if(len(destination) == 0):
            pass
        else:
            new_wishlist = " | ".join(destination)
        try:
            # save to config file
            config['members'][str(user.usrnum)][SantaBotConstants.WISHLISTURL] = new_wishlist
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
async def getwishlisturl(ctx: commands.Context):
    '''
    Get current wishlist
    '''
    currAuthor = ctx.author
    global usr_list
    if SantaBotHelper.user_is_participant(ctx.author.id, usr_list):
        (index, user) = SantaBotHelper.get_participant_object(ctx.author.id, usr_list)
        try:
            await currAuthor.send("Current wishlist destination(s): {0}".format(user.wishlisturl))
        except:
            await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return

@bot.command()
async def setprefs(ctx: commands.Context, *preferences:str):
    '''
    Set new preferences
    '''
    currAuthor = ctx.author
    global usr_list
    if SantaBotHelper.user_is_participant(currAuthor.id, usr_list):
        if(SantaBotHelper.channelIsPrivate(ctx.channel)):
            pass
        else:
            await ctx.message.delete()
        (index, user) = SantaBotHelper.get_participant_object(currAuthor, usr_list)
        new_prefs = "None"
        if(len(preferences) == 0):
            pass
        else:
            new_prefs = " | ".join(preferences)
        try:
            #save to config file
            config['members'][str(user.usrnum)][SantaBotConstants.PREFERENCES] = str(new_prefs)
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
async def getprefs(ctx: commands.Context):
    '''
    Get current preferences
    '''
    currAuthor = ctx.author
    global usr_list
    if SantaBotHelper.user_is_participant(ctx.author.id, usr_list):
        (index, user) = SantaBotHelper.get_participant_object(ctx.author.id, usr_list)
        try:
            await currAuthor.send("Current preference(s): {0}".format(user.preferences))
        except:
            await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return

@bot.command()
async def start(ctx: commands.Context):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    global usr_list
    global exchange_started
    global is_paused
    if(currAuthor.top_role == ctx.guild.roles[-1]):
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
            potential_list = SantaBotHelper.propose_partner_list(usr_list)
            while(not SantaBotHelper.partners_are_valid(potential_list)):
                print("Proposing a partner list")
                potential_list = SantaBotHelper.propose_partner_list(usr_list)
            # save to config file
            print("Partner assignment successful")
            for user in potential_list:
                (temp_index, temp_user) = SantaBotHelper.get_participant_object(user.idstr, usr_list)
                (index, partner) = SantaBotHelper.get_participant_object(user.partnerid, potential_list)
                temp_user.partnerid = user.partnerid
                config['members'][str(user.usrnum)][SantaBotConstants.PARTNERID] = user.partnerid
                config.write()
                # tell participants who their partner is
                this_user = ctx.guild.get_member(int(user.idstr))
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
        await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
    return

@bot.command()
async def restart(ctx: commands.Context):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    global usr_list
    global exchange_started
    global is_paused
    is_paused = True
    if((currAuthor.top_role == ctx.guild.roles[-1]) and is_paused):
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
        list_changed = SantaBotHelper.usr_list_changed_during_pause(usr_list, user_left_during_pause)
        if(list_changed):
            ctx.send("User list changed during the pause. Partners must be picked again with `{0}start`.".format(CONFIG.prefix))
        else:
            exchange_started = True
            is_paused = False
            config['programData']['exchange_started'] = True
            config.write()
            await ctx.send("No change was made during the pause. Secret Santa resumed with the same partners.")
    elif(currAuthor.top_role != ctx.guild.roles[-1]):
        await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
    elif(not is_paused):
        await ctx.send(BOT_ERROR.NOT_PAUSED)
    else:
        await ctx.send(BOT_ERROR.UNREACHABLE)
    return

@bot.command()
async def pause(ctx: commands.Context):
    # TODO: add help menu instruction
    global exchange_started
    global is_paused
    if(ctx.author.top_role == ctx.guild.roles[-1]):
        exchange_started = False
        config['programData']['exchange_started'] = False
        config.write()
        is_paused = True
        await ctx.send("Secret Santa has been paused. New people may now join.")
    else:
        await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
    return

@bot.command()
async def join(ctx: commands.Context):
    '''
    Join Secret Santa if it has not started. Contact the Secret Santa admin if you wish to join.
    '''
    currAuthor = ctx.author
    global usr_list
    global highest_key
    # check if the exchange has already started
    if SantaBotHelper.user_is_participant(currAuthor.id, usr_list):
        await ctx.send(BOT_ERROR.ALREADY_JOINED)
    else:
        # initialize instance of Participant for the author
        highest_key = highest_key + 1
        usr_list.append(Participant(currAuthor.name, currAuthor.discriminator, currAuthor.id, highest_key))
        # write details of the class instance to config and increment total_users
        config['members'][str(highest_key)] = [currAuthor.name, currAuthor.discriminator, currAuthor.id, highest_key, "", "", ""]
        config.write()

        # prompt user about inputting info
        await ctx.send(currAuthor.mention + " has been added to the {0} Secret Santa exchange!".format(str(ctx.guild)) + "\nMore instructions have been DMd to you.")
        try:
            userPrompt = """Welcome to the __{0}__ Secret Santa! Please input your wishlist URL and preferences **(by DMing this bot)** so your Secret Santa can send you something.\n
                Use `{1}setwishlisturl [wishlist urls separated by a space ]` to set your wishlist URL (you may also add your mailing address).\n
                Use `{2}setprefs [preferences separated by a space ]` to set gift preferences for your Secret Santa. Put N/A if none.""".format(str(ctx.guild), CONFIG.prefix, CONFIG.prefix)
            await currAuthor.send(userPrompt)
        except:
            ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
    return

@bot.command()
async def leave(ctx: commands.Context):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    global usr_list
    global is_paused
    global user_left_during_pause
    if(SantaBotHelper.user_is_participant(currAuthor.id, usr_list)):
        (index, user) = SantaBotHelper.get_participant_object(currAuthor.id, usr_list)
        usr_list.remove(user)
        popped_user = config['members'].pop(str(user.usrnum))
        config.write()
        if(is_paused):
            user_left_during_pause = True
        await ctx.send(currAuthor.mention + " has left the {0} Secret Santa exchange".format(str(ctx.guild)))
    else:
        await ctx.send(BOT_ERROR.UNJOINED)
    return

@bot.command()
async def end(ctx: commands.Context):
    # TODO: add help menu instruction
    global usr_list
    global highest_key
    global exchange_started
    global is_paused
    if(ctx.author.top_role == ctx.guild.roles[-1]):
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
        await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
    return

@bot.command()
async def listparticipants(ctx: commands.Context):
    # TODO: add help menu instruction
    global usr_list
    global highest_key
    if(ctx.author.top_role == ctx.guild.roles[-1]):
        if(highest_key == 0):
            await ctx.send("Nobody has signed up for the secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
        else:
            msg = '```The following people are signed up for the Secret Santa exchange:\n'
            for user in usr_list:
                this_user = ctx.guild.get_member(user.idstr)
                msg = msg + str(user.name) + "#" + str(user.discriminator) + "\n"
            msg = msg + "\nUse `{0}join` to enter the exchange.```".format(CONFIG.prefix)
    else:
        await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
    return

@bot.command()
async def totalparticipants(ctx: commands.Context):
    # TODO: add help menu instruction
    global highest_key
    if highest_key == 0:
        await ctx.send("Nobody has signed up for the Secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
    elif highest_key == 1:
        await ctx.send("1 person has signed up for the Secret Santa exchange. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
    else:
        await ctx.send("{0} people have joined the Secret Santa exchange so far. Use `{1}join` to enter the exchange.".format(str(len(usr_list)), CONFIG.prefix))
    return

@bot.command()
async def partnerinfo(ctx: commands.Context):
    # TODO: add help menu instruction
    currAuthor = ctx.author
    global usr_list
    global exchange_started
    authorIsParticipant = SantaBotHelper.user_is_participant(currAuthor.id, usr_list)
    if(exchange_started and authorIsParticipant):
        (usr_index, user) = SantaBotHelper.get_participant_object(currAuthor, usr_list)
        (partner_index, partnerobj) = SantaBotHelper.get_participant_object(user.partnerid, usr_list)
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
@has_permissions(manage_roles=True, ban_members=True)
async def archive_pins(ctx: commands.Context, channel_to_archive: int, channel_to_message: int):
    '''
    Archive the pins in one channel to another channel as messages
    '''
    src_id = channel_to_archive
    dest_id = channel_to_message
    src_channel = bot.get_channel(src_id)
    dest_channel = bot.get_channel(dest_id)
    start_message = "Attempting to archive pinned messages from <#{0}> to <#{1}>".format(src_id, dest_id)
    await ctx.send(content=start_message)
    pins_to_archive = await src_channel.pins()
    pins_to_archive.reverse()

    for pin in pins_to_archive:
        attachments = pin.attachments
        attachment_str = ""
        for attachment in attachments:
            attachment_str += "{0}\n".format(attachment.url) # add link to attachments

        pin_author = pin.author.name
        pin_datetime = pin.created_at.strftime("%B %d, %Y")
        pin_url = pin.jump_url
        pin_content = pin.content
        output_str = "-**(from `{0}` on {1})** {2}\n".format(pin_author, pin_datetime, pin_content)
        output_str += "Message link: <{0}>\n".format(pin_url)
        if not attachment_str:
            output_str += "Attachment links: {0}".format(attachment_str)
        if len(output_str) > 2000:
            await ctx.send(content=BOT_ERROR.ARCHIVE_ERROR_LENGTH(pin_url))
        else:
            await dest_channel.send(content=output_str)
    
    end_message = "Pinned message are archived in <#{0}>. If the archive messages look good, use __{1}unpin_all__ to remove the pins in <#{2}>".format(dest_id, CONFIG.prefix, src_id)
    await ctx.send(content=end_message)

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def unpin_all(ctx: commands.Context, channel_id_to_unpin: int = -1):
    '''
    Unpins all the pinned messages in the channel. Called to clean up after archive_pins.
    '''
    if channel_id_to_unpin == -1:
        channel_id_to_unpin = ctx.channel.id
    
    remove_channel = await bot.get_channel(channel_id_to_unpin)
    start_message = "Attempting to remove all pinned messages."
    await ctx.send(content=start_message)
    pins_to_remove = await remove_channel.pins()
    for pin in pins_to_remove:
        await pin.unpin()
    end_message = "All pinned messages removed."
    await ctx.send(content=end_message)

@bot.command()
async def invite(ctx: commands.Context):
    link = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=67185664".format(CONFIG.client_id)
    await ctx.send_message("Bot invite link: {0}".format(link))

ROLE_CHANNEL = 461740709062377473
async def manage_reactions(payload, add):
    message_id = payload.message_id
    channel_id = payload.channel_id
    emoji = payload.emoji
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
 
    if channel_id == ROLE_CHANNEL:
        channel = discord.utils.get(bot.get_all_channels(), id=channel_id)
        async for message in channel.history(limit=200):
            if message.id == message_id:
                break
 
        content = message.content.split("\n")
        for line in content:
            l = line.split(" ")
            for c, word in enumerate(l):
                if word == "for" and c > 0 and l[c-1] == str(emoji):
                    role_id = l[c+1][3:-1]
                    role = guild.get_role(int(role_id))
                    if add:
                        await user.add_roles(role)
                    else:
                        await user.remove_roles(role)

@unpin_all.error
@archive_pins.error
async def pin_archive_error(error, ctx):
    if isinstance(error, MissingPermissions):
        text = BOT_ERROR.NO_PERMISSION("mod")
        await ctx.send(content=text)
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(content=BOT_ERROR.MISSING_ARGUMENTS)
    else:
        await ctx.send(content="Error: undetermined please contact <@224949031514800128>")


@bot.event
async def on_raw_reaction_add(payload):
    await manage_reactions(payload, True)
 
@bot.event
async def on_raw_reaction_remove(payload):
    await manage_reactions(payload, False)

bot.run(CONFIG.discord_token, reconnect = True)
