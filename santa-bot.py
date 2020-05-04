import datetime
import logging
import os

import discord
from configobj import ConfigObj
from discord.ext import commands

import CONFIG
from cogs.SecretSanta import SecretSanta
from cogs.SantaAdministrative import SantaAdministrative
from cogs.SantaMiscellaneous import SantaMiscellaneous

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
    currentDT = datetime.datetime.now()
    print('------')
    print (currentDT.strftime("%Y-%m-%d %H:%M:%S"))
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity = discord.Game(name = CONFIG.prefix + "help"))
    print('------')

def start_santa_bot():
    bot.add_cog(SecretSanta(bot, config))
    bot.add_cog(SantaAdministrative(bot))
    bot.add_cog(SantaMiscellaneous(bot))
    bot.run(CONFIG.discord_token, reconnect = True)

if __name__ == '__main__':
    start_santa_bot()
