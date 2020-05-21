import logging
import os

from configobj import ConfigObj
from discord.ext import commands

import CONFIG
from cogs.SecretSanta import SecretSanta
from cogs.SantaAdministrative import SantaAdministrative
from cogs.SantaMiscellaneous import SantaMiscellaneous
from helpers.SQLiteHelper import SQLiteHelper

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename=CONFIG.dbg_path, encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)
bot = commands.Bot(command_prefix = CONFIG.prefix)

def start_santa_bot():
    #initialize config file
    config = None
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

    # initialize the SQLite db
    sqlitehelper = SQLiteHelper(CONFIG.sqlite_path)
    sqlitehelper.create_connection()

    bot.add_cog(SecretSanta(bot, config))
    bot.add_cog(SantaAdministrative(bot, sqlitehelper))
    bot.add_cog(SantaMiscellaneous(bot))
    bot.run(CONFIG.discord_token, reconnect = True)

if __name__ == '__main__':
    start_santa_bot()
