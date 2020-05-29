import pendulum

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument
from discord import Game as discordGame

import CONFIG
import helpers.BOT_ERROR as BOT_ERROR
from helpers.SQLiteHelper import SQLiteHelper

class SantaAdministrative(commands.Cog, name='Administrative'):
    def __init__(self, bot: commands.Bot, sqlitehelper: SQLiteHelper):
        self.bot = bot
        self.role_channel = bot.get_channel(CONFIG.role_channel) if (CONFIG.role_channel != -1) else None
        self.sqlhelp = sqlitehelper
        self.sqlhelp.create_table("Countdowns", "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, time TEXT NOT NULL, user_id INTEGER NOT NULL, UNIQUE(name))")

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def assign_role_channel(self, ctx: commands.Context, reaction_role_channel: discord.TextChannel = None):
        '''
        Not recommended. Allows a reaction role channel to be assigned.
        The recommended route is to set the role_channel variable in the bot's config file to the channel ID you want.
        '''
        if reaction_role_channel != None:
            self.role_channel = reaction_role_channel # use given channel
        else:
            if(isinstance(ctx.channel, discord.PrivateChannel)):
                await ctx.send(content=BOT_ERROR.REACTION_ROLE_UNASSIGNED)
            else:
                self.role_channel = ctx.channel # use current channel
        
        if(self.role_channel != None):
            await ctx.send(content="Reaction role channel assigned to {0}".format(self.role_channel.mention))

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def archive_pins(self, ctx: commands.Context, channel_to_archive: discord.TextChannel, channel_to_message: discord.TextChannel):
        '''
        Archive the pins in one channel to another channel as messages
        '''

        start_message = "Attempting to archive pinned messages from {0} to {1}".format(channel_to_archive.mention, channel_to_message.mention)
        await ctx.send(content=start_message)

        pins_to_archive = await channel_to_archive.pins()
        pins_to_archive.reverse()

        for pin in pins_to_archive:
            attachments = pin.attachments
            attachment_str = ""
            for attachment in attachments:
                attachment_str += "{0}\n".format(attachment.url) # add link to attachments

            pin_author = pin.author.name
            pin_pendulum = pendulum.instance(pin.created_at)
            pin_dt_str = pin_pendulum.format("MMMM DD, YYYY")

            pin_url = pin.jump_url
            pin_content = pin.content
            output_str = "-**(from `{0}` on {1})** {2}\n".format(pin_author, pin_dt_str, pin_content)
            output_str += "Message link: <{0}>\n".format(pin_url)
            output_str += "Attachment links: {0}".format(attachment_str)
            if len(output_str) > 2000:
                await ctx.send(content=BOT_ERROR.ARCHIVE_ERROR_LENGTH(pin_url))
            else:
                await channel_to_message.send(content=output_str)
        
        end_message = "Pinned message are archived in {0}. If the archive messages look good, use **{1}unpin_all** to remove the pins in {2}".format(channel_to_message.mention, CONFIG.prefix, channel_to_archive.mention)
        await ctx.send(content=end_message)

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def unpin_all(self, ctx: commands.Context, channel_to_unpin: discord.TextChannel = None):
        '''
        Unpins all the pinned messages in the channel. Called to clean up after archive_pins.
        Defaults to the channel in which it's called.
        '''
        if(channel_to_unpin == None):
            channel_to_unpin = ctx.channel()
        
        start_message = "Attempting to remove all pinned messages from {0}.".format(channel_to_unpin.mention)
        await ctx.send(content=start_message)
        if(channel_to_unpin == None):
            await ctx.send(BOT_ERROR.INACCESSIBLE_CHANNEL)
            return
        pins_to_remove = await channel_to_unpin.pins()
        for pin in pins_to_remove:
            await pin.unpin()
        end_message = "All pinned messages removed from {0}.".format(channel_to_unpin.mention)
        await ctx.send(content=end_message)

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

        expected_pend_format = "MM/D/YY [@] h:m A Z"
        cd_table_name = "Countdowns"
        args = arg.split(sep="|") # minimum separator if the user misses a space somewhere (spaces stripped in next few lines)
        countdown_name = ""
        countdown_time = ""
        if(len(args) > 0):
            countdown_name = args[0].strip()
        if(len(args) > 1):
            countdown_time = args[1].strip()

        cd_hints = self.find_countdown_hints(command, countdown_name, countdown_time)
        if(cd_hints != ""):
            await ctx.send(cd_hints)
            return
        
        relay_message = ""
        if(command == "set"):
            relay_message = self.countdown_cmd_set(ctx, expected_pend_format, cd_table_name, countdown_name, countdown_time)
        elif(command == "change"):
            relay_message = self.countdown_cmd_change(ctx, expected_pend_format, cd_table_name, countdown_name, countdown_time)
        elif(command == "check"):
            relay_message = self.countdown_cmd_check(expected_pend_format, cd_table_name, countdown_name)
        elif(command == "remove"):
            relay_message = self.countdown_cmd_remove(ctx, expected_pend_format, cd_table_name, countdown_name)
        elif(command == "list"):
            relay_message = self.countdown_cmd_list(ctx, expected_pend_format, cd_table_name)
        elif(command == "clean"):
            relay_message = self.countdown_cmd_clean(expected_pend_format, cd_table_name)
        else:
            relay_message = BOT_ERROR.INVALID_COUNTDOWN_COMMAND

        await ctx.send(content=relay_message)

    def countdown_cmd_set(self, ctx: commands.Context, pend_format: str, cd_table_name: str, cd_name: str, cd_time: str):
        result_str = ""
        try:
            pend_test_convert = pendulum.from_format(cd_time, pend_format) # check that the format is correct
            if(self.sqlhelp.insert_records(cd_table_name, "(name, time, user_id)", ["('{0}', '{1}', {2})".format(cd_name, cd_time, ctx.author.id)])):
                diff_str = self.find_pend_diff_str(pend_test_convert)
                result_str = "{0} countdown set for {1} ({2})".format(cd_name, cd_time, diff_str)
            else:
                result_str = BOT_ERROR.COUNTDOWN_NAME_TAKEN
        except ValueError as error:
            expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
            result_str = expected + "ex. `5/17/20 @ 1:00 PM -06:00`"
            print(result_str)
        finally:
            return result_str
    
    def countdown_cmd_change(self, ctx: commands.Context, pend_format: str, cd_table_name: str, cd_name: str, cd_time: str):
        result_str = ""
        try:
            pend_test_convert = pendulum.from_format(cd_time, pend_format) # check that the format is correct
        except ValueError as error:
            expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
            result_str = expected + " ex. `5/17/20 @ 1:00 PM -06:00`"
            print(result_str)
            return result_str
        
        query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, cd_name)
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            if(len(query_result) > 0):
                (query_id, query_name, query_time, query_user_id) = query_result[0]
                if(ctx.author.id == query_user_id):
                    if(self.sqlhelp.execute_update_query(cd_table_name, "time=\'{0}\'".format(cd_time), "id={0}".format(query_id))):
                        diff_str = self.find_pend_diff_str(pend_test_convert)
                        result_str = "Updated countdown for {0}. Now set for {1}".format(cd_name, diff_str)
                    else:
                        result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
                else:
                    cd_owner = ctx.guild.get_member(query_user_id)
                    result_str = BOT_ERROR.CANNOT_CHANGE_COUNTDOWN(cd_owner.name)
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)

        return result_str

    def countdown_cmd_check(self, pend_format: str, cd_table_name: str, cd_name: str):
        result_str = ""
        query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, cd_name)
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            (query_id, query_name, query_time, query_user_id) = query_result[0]
            cd_pend = pendulum.from_format(query_time, pend_format)
            diff_str = self.find_pend_diff_str(cd_pend)
            result_str = "Time until {0}: {1}".format(cd_name, diff_str)
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
        return result_str

    def countdown_cmd_remove(self, ctx: commands.Context, pend_format: str, cd_table_name: str, cd_name: str):
        result_str = ""
        query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, cd_name)
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            (query_id, query_name, query_time, query_user_id) = query_result[0]
            if(query_user_id == ctx.author.id):
                if(self.sqlhelp.execute_delete_query(cd_table_name, "id={0}".format(query_id))):
                    result_str = "Countdown timer `{0}` removed.".format(query_name)
                else:
                    result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
            else:
                cd_owner = ctx.guild.get_member(query_user_id)
                result_str = BOT_ERROR.CANNOT_CHANGE_COUNTDOWN(cd_owner.name)
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
        return result_str

    def countdown_cmd_list(self, ctx: commands.Context, pend_format: str, cd_table_name: str):
        result_str = ""
        query_get_all_timers = "SELECT * FROM {0};".format(cd_table_name)
        query_results = self.sqlhelp.execute_read_query(query_get_all_timers)
        result_str = "Countdown Name | Owner | Time | Time Until\n"
        if(query_results != None):
            for (query_id, query_name, query_time, query_user_id) in query_results:
                cd_pend = pendulum.from_format(query_time, pend_format) # convert to pendulum
                diff_str = self.find_pend_diff_str(cd_pend)
                time_until_str = "Time until {0}: {1}".format(query_name, diff_str)
                cd_owner = ctx.guild.get_member(query_user_id).name
                result_str += "{0} | {1} | {2} | {3}\n".format(query_name, cd_owner, query_time, time_until_str)
        return result_str

    def countdown_cmd_clean(self, pend_format: str, cd_table_name: str):
        result_str = ""
        query_get_all_timers = "SELECT * FROM {0};".format(cd_table_name)
        query_results = self.sqlhelp.execute_read_query(query_get_all_timers) # get all the countdowns
        if(query_results != None):
            for (query_id, query_name, query_time, query_user_id) in query_results:
                if(not pendulum.from_format(query_time, pend_format).is_future()): # if the countdown has passed, delete
                    result_str += "{0} has passed. Deleting {1} countdown.\n".format(query_time, query_name)
                    self.sqlhelp.execute_delete_query(cd_table_name, "id = {0}".format(query_id))
        return result_str

    def find_countdown_hints(self, cd_command: str, cd_name: str, cd_time: str):
        '''
        Get argument hints based on the command input and user input - only called from SantaAdministrative.countdown()
        '''
        missing_args_str = "Missing argument(s):"
        missing_name_str = "<timer name>"
        missing_time_str = "<formatted time>"
        missing_time_hint = "Formatted time ex. `5/17/20 @ 1:00 PM -06:00`"
        complete_command_str = "Complete command: `{0}countdown {1}".format(CONFIG.prefix, cd_command)
        argument_help = ""
        if(cd_command == "set"):
            if(cd_name == ""):
                argument_help = "{0} {1} | {2}\n{3}\n".format(missing_args_str, missing_name_str, missing_time_str, missing_time_hint)
                argument_help += "{0} {1} | {2}`".format(complete_command_str, missing_name_str, missing_time_str)
            elif(cd_time == ""):
                argument_help = "{0} {1}\n{2}".format(missing_args_str, missing_time_str, missing_time_hint)
                argument_help += "{0} {1} | {2}`".format(complete_command_str, cd_name, missing_time_str)
        elif(cd_command == "change"):
            if(cd_name == ""):
                argument_help = "{0} {1} | {2}\n{3}\n".format(missing_args_str, missing_name_str, missing_time_str, missing_time_hint)
                argument_help += "{0} {1} | {2}`".format(complete_command_str, missing_name_str, missing_time_str)
            elif(cd_time == ""):
                argument_help = "{0} {1}\n{2}".format(missing_args_str, missing_time_str, missing_time_hint)
                argument_help += "{0} {1} | {2}`".format(complete_command_str, cd_name, missing_time_str)
        elif(cd_command == "check"):
            if(cd_name == ""):
                argument_help = "{0} {1}".format(missing_args_str, missing_name_str)
                argument_help += "{0} {1}`".format(complete_command_str, missing_name_str)
        elif(cd_command == "remove"):
            if(cd_name == ""):
                argument_help = "{0} {1}".format(missing_args_str, missing_name_str)
                argument_help += "{0} {1}`".format(complete_command_str, missing_name_str)
        elif(cd_command == "list"):
            pass
        elif(cd_command == "clean"):
            pass
        return argument_help

    def find_pend_diff_str(self, pend: pendulum.DateTime):
        cd_diff = pend.diff(pendulum.now())
        (diff_days, diff_hours, diff_minutes) = (cd_diff.days, cd_diff.hours, cd_diff.minutes)
        if(not pend.is_future()):
            (diff_days, diff_hours, diff_minutes) = (-diff_days, -diff_hours, -diff_minutes)
        diff_str = "{0} days, {1} hours, {2} minutes from now".format(diff_days, diff_hours, diff_minutes)
        return diff_str

    @unpin_all.error
    @archive_pins.error
    async def pin_archive_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = BOT_ERROR.NO_PERMISSION("mod")
            await ctx.send(content=text)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(content=BOT_ERROR.MISSING_ARGUMENTS)
        elif isinstance(error, commands.CommandError):
            await ctx.send(content=error)
        else:
            await ctx.send(content=BOT_ERROR.UNDETERMINED_CONTACT_CODE_OWNER)

    @commands.Cog.listener(name='on_raw_reaction_add')
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def manage_reactions(self, payload: discord.RawReactionActionEvent):
        if(self.role_channel == None): # if no role channel assigned,
            self.role_channel = self.bot.get_channel(CONFIG.role_channel) if (CONFIG.role_channel != -1) else None # attempt to get role channel
            if(self.role_channel == None): # if that fails (CONFIG.role_channel == -1 or get_channel fails)
                print(BOT_ERROR.REACTION_ROLE_UNASSIGNED) # throw failure message
                return # end command
            else:
                pass # reassignment of role_channel worked
        else:
            pass # role_channel is assigned

        message_id = payload.message_id
        channel_id = payload.channel_id
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
    
        if channel_id == self.role_channel.id:
            message = None
            async for message in self.role_channel.history(limit=200):
                if message.id == message_id:
                    break
    
            if message != None:
                content = message.content.split("\n")
                for line in content:
                    l = line.split(" ")
                    for c, word in enumerate(l):
                        if word == "for" and c > 0 and l[c-1] == str(emoji):
                            role_id = l[c+1][3:-1]
                            role = guild.get_role(int(role_id))
                            if payload.event_type == "REACTION_ADD":
                                await user.add_roles(role)
                            else:
                                await user.remove_roles(role)

    @commands.Cog.listener(name='on_ready')
    async def nice_ready_print(self):
        """print message when client is connected"""
        currentDT = pendulum.now()
        print('------')
        print (currentDT.format("YYYY-MM-D H:mm:ss"))
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        await self.bot.change_presence(activity = discordGame(name = CONFIG.prefix + "help"))
        print('------')
