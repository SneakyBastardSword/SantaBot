import logging

from discord.ext import commands
import discord

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
    async def emote(self, ctx: commands.Context, *emotes: discord.PartialEmoji):
        '''
        Get the URL to emotes without needing to open the link. Custom emotes only.
        '''
        for passed_emote in emotes:
            emote_url = str(passed_emote.url)
            emote_name = passed_emote.name
            emote_id = passed_emote.id
            img_type = "gif" if passed_emote.animated else "png"
            BOT_ERROR.output_info(f"Name={emote_name}, ID={emote_id}, IMG_TYPE={img_type}, url={emote_url}", self.logger)
            await ctx.send(content=emote_url)
        return
