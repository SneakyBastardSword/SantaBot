import urllib3

from discord.ext import commands

import CONFIG
from helpers.SantaCountdownHelper import SantaCountdownHelper
from helpers.SQLiteHelper import SQLiteHelper

class SantaUtilities(commands.Cog, name='Utilities'):
    def __init__(self, bot: commands.Bot, sqlitehelper: SQLiteHelper):
        self.bot = bot
        self.cd_helper = SantaCountdownHelper(sqlitehelper)

    @commands.command(aliases=['cd'])
    async def countdown(self, ctx: commands.Context, command: str="", *, arg=""):
        '''
        Add a countdown timer
        Commands: set, change, check, list, remove, clean
        '''
        if(command == ""):
            usage_guide = "Proper usage: `{0}<countdown|cd> <set|change|check|list|remove|clean> <arguments>`\n".format(CONFIG.prefix)
            usage_guide += "Use each sub-command (`{0}<countdown|cd> <set|change|check|list|remove|clean>`) for more information on the necessary arguments".format(CONFIG.prefix)
            await ctx.send(usage_guide)
            return

        args = arg.split(sep="|") # minimum separator if the user misses a space somewhere (spaces stripped in next few lines)
        countdown_name = ""
        countdown_time = ""
        if(len(args) > 0):
            countdown_name = args[0].strip()
        if(len(args) > 1):
            countdown_time = args[1].strip()

        relay_message = self.cd_helper.run_countdown_command(ctx, command, countdown_name, countdown_time)

        await ctx.send(content=relay_message)
        return

    @commands.command()
    async def emote(self, ctx: commands.Context, *emotes: str):
        '''
        Get the URL to emotes without needing to open the link.
        '''
        http = urllib3.PoolManager()
        for passed_emote in emotes:
            # Create the base URL of the emote
            emote_parts = passed_emote.split(sep=":")
            (emote_name, emote_id) = (emote_parts[1], (emote_parts[2])[:-1])
            base_url = "https://cdn.discordapp.com/emojis/{0}".format(str(emote_id))

            # http request to find the appropriate extension
            response = http.urlopen('GET', url=base_url)
            img_type = response.info()['Content-Type']
            img_ext = img_type.split(sep="/")[1]
            http.clear()

            # output
            emote_url = "{0}.{1}".format(base_url, img_ext)
            print("Name={0}, ID={1}, IMG_TYPE={2}".format(emote_name, emote_id, img_type))
            await ctx.send(content=emote_url)
        return
