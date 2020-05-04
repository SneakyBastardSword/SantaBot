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
        output_str += "Attachment links: {0}".format(attachment_str)
        if len(output_str) > 2000:
            await ctx.send(content=BOT_ERROR.ARCHIVE_ERROR_LENGTH(pin_url))
        else:
            await dest_channel.send(content=output_str)
    
    end_message = "Pinned message are archived in <#{0}>. If the archive messages look good, use **{1}unpin_all** to remove the pins in <#{2}>".format(dest_id, CONFIG.prefix, src_id)
    await ctx.send(content=end_message)

@bot.command()
@has_permissions(manage_roles=True, ban_members=True)
async def unpin_all(ctx: commands.Context, channel_id_to_unpin: int = -1):
    '''
    Unpins all the pinned messages in the channel. Called to clean up after archive_pins.
    Defaults to the channel in which it's called.
    '''
    print(channel_id_to_unpin)
    if channel_id_to_unpin == -1:
        channel_id_to_unpin = ctx.channel.id
    
    remove_channel = bot.get_channel(channel_id_to_unpin)
    start_message = "Attempting to remove all pinned messages from <#{0}>.".format(channel_id_to_unpin)
    await ctx.send(content=start_message)
    pins_to_remove = await remove_channel.pins()
    for pin in pins_to_remove:
        await pin.unpin()
    end_message = "All pinned messages removed from <#{0}>.".format(channel_id_to_unpin)
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
