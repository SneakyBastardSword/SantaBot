import urllib3
import logging

from discord.ext import commands

import CONFIG
import helpers.BOT_ERROR as BOT_ERROR
from helpers.SantaCountdownHelper import SantaCountdownHelper
from helpers.SQLiteHelper import SQLiteHelper

class SantaUtilities(commands.Cog, name='Utilities'):
    def __init__(self, bot: commands.Bot, sqlitehelper: SQLiteHelper):
        self.bot = bot
        self.cd_helper = SantaCountdownHelper(sqlitehelper)
        self.logger = logging.getLogger(name="SantaBot.SantaUtilities")
        self.logger.info("Creating cog")

    @commands.command(aliases=['cd'])
    async def countdown(self, ctx: commands.Context, command: str="", *, arg=""):
        '''
        Add a countdown timer
        Commands: set, change, check, list, remove, clean
        '''
        if(command == ""):
            usage_guide = f"Proper usage: `{CONFIG.prefix}<countdown|cd> <set|change|check|list|remove|clean> <arguments>`\n"
            usage_guide += f"Use each sub-command (`{CONFIG.prefix}<countdown|cd> <set|change|check|list|remove|clean>`) for more information on the necessary arguments"
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
            base_url = f"https://cdn.discordapp.com/emojis/{str(emote_id)}"

            # http request to find the appropriate extension
            response = http.urlopen('GET', url=base_url)
            img_type = response.info()['Content-Type']
            img_ext = img_type.split(sep="/")[1]
            http.clear()

            # output
            emote_url = f"{base_url}.{img_ext}"
            BOT_ERROR.output_info(f"Name={emote_name}, ID={emote_id}, IMG_TYPE={img_type}, url={emote_url}")
            await ctx.send(content=emote_url)
        return
