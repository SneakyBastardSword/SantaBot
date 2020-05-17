import pendulum

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument
from discord import RawReactionActionEvent
from discord import Game as discordGame

import CONFIG
import helpers.BOT_ERROR as BOT_ERROR
from helpers.SQLiteHelper import SQLiteHelper

class SantaAdministrative(commands.Cog, name='Administrative'):
    def __init__(self, bot: commands.Bot, sqlitehelper: SQLiteHelper):
        self.bot = bot
        self.role_channel = CONFIG.role_channel
        self.sqlhelp = sqlitehelper
        self.sqlhelp.create_table("Countdowns", "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, time TEXT NOT NULL, user_id INTEGER NOT NULL, UNIQUE(name))")

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def assign_role_channel(self, ctx: commands.Context, reaction_role_channel: int):
        '''
        Not recommended. Allows a reaction role channel to be assigned.
        The recommended route is to set the role_channel variable in the bot's config file to the channel ID you want.
        '''
        dest_channel = ctx.guild.get_channel(reaction_role_channel)
        self.role_channel = reaction_role_channel
        if dest_channel != None:
            await ctx.send(content="Reaction role channel assigned to <#{0}>".format(self.role_channel))
        else:
            await ctx.send(content=BOT_ERROR.REACTION_ROLE_UNASSIGNED)

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def archive_pins(self, ctx: commands.Context, channel_to_archive: int, channel_to_message: int):
        '''
        Archive the pins in one channel to another channel as messages
        '''
        src_id = channel_to_archive
        dest_id = channel_to_message
        src_channel = ctx.guild.get_channel(src_id)
        dest_channel = ctx.guild.get_channel(dest_id)

        start_message = "Attempting to archive pinned messages from <#{0}> to <#{1}>".format(src_id, dest_id)
        await ctx.send(content=start_message)
        if((src_channel == None) or (dest_channel == None)):
            await ctx.send(BOT_ERROR.INACCESSIBLE_CHANNEL)
            return
        pins_to_archive = await src_channel.pins()
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
                await dest_channel.send(content=output_str)
        
        end_message = "Pinned message are archived in <#{0}>. If the archive messages look good, use **{1}unpin_all** to remove the pins in <#{2}>".format(dest_id, CONFIG.prefix, src_id)
        await ctx.send(content=end_message)

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def unpin_all(self, ctx: commands.Context, channel_id_to_unpin: int = -1):
        '''
        Unpins all the pinned messages in the channel. Called to clean up after archive_pins.
        Defaults to the channel in which it's called.
        '''
        print(channel_id_to_unpin)
        if channel_id_to_unpin == -1:
            channel_id_to_unpin = ctx.channel.id
        
        remove_channel = ctx.guild.get_channel(channel_id_to_unpin)
        start_message = "Attempting to remove all pinned messages from <#{0}>.".format(channel_id_to_unpin)
        await ctx.send(content=start_message)
        if(remove_channel == None):
            await ctx.send(BOT_ERROR.INACCESSIBLE_CHANNEL)
            return
        pins_to_remove = await remove_channel.pins()
        for pin in pins_to_remove:
            await pin.unpin()
        end_message = "All pinned messages removed from <#{0}>.".format(channel_id_to_unpin)
        await ctx.send(content=end_message)

    @commands.command(aliases=['cd'])
    async def countdown(self, ctx: commands.Context, command: str, *, arg=""):
        expected_pend_format = "MM/D/YY [@] h:m A Z"
        cd_table_name = "Countdowns"
        args = arg.split(sep=" | ")
        countdown_name = args[0]
        countdown_time = ""
        if(len(args) > 1):
            countdown_time = args[1]
        if(command == "set"):
            try:
                pend_test_convert = pendulum.from_format(countdown_time, expected_pend_format) # check that the format is correct
                if(self.sqlhelp.insert_records(cd_table_name, "(name, time, user_id)", ["('{0}', '{1}', {2})".format(countdown_name, countdown_time, ctx.author.id)])):
                    await ctx.send("{0} countdown set for {1} ({2})".format(countdown_name, countdown_time, pend_test_convert.diff_for_humans(pendulum.now())))
            except ValueError as error:
                expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
                error_str = expected + " ex. `5/17/20 @ 1:00 PM -06:00`"
                print(error_str)
                await ctx.send(error_str)
                return
        elif(command == "change"):
            try:
                pend_test_convert = pendulum.from_format(countdown_time, expected_pend_format) # check that the format is correct
            except ValueError as error:
                expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
                error_str = expected + " ex. `5/17/20 @ 1:00 PM -06:00`"
                print(error_str)
                await ctx.send(error_str)
                return
            
            query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, countdown_name)
            query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
            if(query_result != None):
                if(len(query_result) > 0):
                    (query_id, query_name, query_time, query_user_id) = query_result[0]
                    if(ctx.author.id == query_user_id):
                        if(self.sqlhelp.execute_update_query(cd_table_name, "time=\'{0}\'".format(countdown_time), "id={0}".format(query_id))):
                            await ctx.send("Updated countdown for {0}".format(countdown_name))
                        else:
                            await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_NAME(countdown_name))
                    else:
                        cd_owner = ctx.guild.get_member(query_user_id)
                        await ctx.send(BOT_ERROR.CANNOT_CHANGE_COUNTDOWN(cd_owner.name))
            else:
                await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_NAME(countdown_name))
        elif(command == "check"):
            query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, countdown_name)
            query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
            if(query_result != None):
                (query_id, query_name, query_time, query_user_id) = query_result[0]
                cd_pend = pendulum.from_format(query_time, expected_pend_format)
                now_dt = pendulum.now()
                cd_diff = cd_pend.diff(now_dt)
                output = "Time until {0}: {1} days, {2} hours, {3} minutes".format(countdown_name, cd_diff.days, cd_diff.hours, cd_diff.minutes)
                await ctx.send(output)
            else:
                await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_NAME(countdown_name))
        elif(command == "list"):
            query_get_all_timers = "SELECT * FROM {0};".format(cd_table_name)
            query_results = self.sqlhelp.execute_read_query(query_get_all_timers)
            output = "Name | Time | Time Until\n"
            if(query_results != None):
                for (query_id, query_name, query_time, query_user_id) in query_results:
                    cd_pend = pendulum.from_format(query_time, expected_pend_format)
                    output += "{0} | {1} | {2} now\n".format(query_name, query_time, cd_pend.diff_for_humans(pendulum.now()))
                    await ctx.send(output)
        elif(command == "remove"):
            query_get_timer_by_name = "SELECT * FROM {0} WHERE name=\'{1}\';".format(cd_table_name, countdown_name)
            query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
            if(query_result != None):
                (query_id, query_name, query_time, query_user_id) = query_result[0]
                if(self.sqlhelp.execute_delete_query(cd_table_name, "id=query_user_id")):
                    await ctx.send("Countdown timer removed.")
                else:
                    await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_NAME(countdown_name))
            else:
                await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_NAME(countdown_name))
        elif(command == "clean"):
            query_get_all_timers = "SELECT * FROM {0};".format(cd_table_name)
            query_results = self.sqlhelp.execute_read_query(query_get_all_timers) # get all the countdowns
            if(query_results != None):
                for (query_id, query_name, query_time, query_user_id) in query_results:
                    if(not pendulum.from_format(query_time, expected_pend_format).is_future()): # if the countdown as passed, delete
                        self.sqlhelp.execute_delete_query(cd_table_name, "id = {0}".format(query_id))
        else:
            await ctx.send(BOT_ERROR.INVALID_COUNTDOWN_COMMAND)

    @unpin_all.error
    @archive_pins.error
    async def pin_archive_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = BOT_ERROR.NO_PERMISSION("mod")
            await ctx.send(content=text)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(content=BOT_ERROR.MISSING_ARGUMENTS)
        else:
            await ctx.send(content=BOT_ERROR.UNDETERMINED_CONTACT_CODE_OWNER)

    @commands.Cog.listener(name='on_raw_reaction_add')
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def manage_reactions(self, payload: RawReactionActionEvent):
        if(self.role_channel == -1):
            print(BOT_ERROR.REACTION_ROLE_UNASSIGNED)
            return

        message_id = payload.message_id
        channel_id = payload.channel_id
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
    
        if channel_id == self.role_channel:
            channel = self.bot.get_channel(self.role_channel)
            message = None
            async for message in channel.history(limit=200):
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
