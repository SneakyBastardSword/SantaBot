import pendulum

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument
from discord import Game as discordGame

import CONFIG
import helpers.BOT_ERROR as BOT_ERROR

class SantaAdministrative(commands.Cog, name='Administrative'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_channel = bot.get_channel(CONFIG.role_channel) if (CONFIG.role_channel != -1) else None

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
            await ctx.send(content=f"Reaction role channel assigned to {reaction_role_channel.name}")

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def archive_pins(self, ctx: commands.Context, channel_to_archive: discord.TextChannel, channel_to_message: discord.TextChannel):
        '''
        Archive the pins in one channel to another channel as messages

        ex. `s!archive_pins #general #archive`
        '''

        start_message = f"Attempting to archive pinned messages from {channel_to_archive.mention} to {channel_to_message.mention}"
        await ctx.send(content=start_message)

        pins_to_archive = await channel_to_archive.pins()
        pins_to_archive.reverse()

        for pin in pins_to_archive:
            attachments = pin.attachments
            attachment_str = ""
            for attachment in attachments:
                attachment_str += f"{attachment.url}\n" # add link to attachments

            pin_author = pin.author.name
            pin_pendulum = pendulum.instance(pin.created_at)
            pin_dt_str = pin_pendulum.format("MMMM DD, YYYY")

            pin_url = pin.jump_url
            pin_content = pin.content
            output_str = f"-**(from `{pin_author}` on {pin_dt_str})** {pin_content}\n"
            output_str += f"Message link: <{pin_url}>\n"
            output_str += f"Attachment links: {attachment_str}"
            if len(output_str) > 2000:
                await ctx.send(content=BOT_ERROR.ARCHIVE_ERROR_LENGTH(pin_url))
            else:
                await channel_to_message.send(content=output_str)
        
        end_message = f"Pinned message are archived in {channel_to_message.mention}. If the archive messages look good, use **{CONFIG.prefix}unpin_all** to remove the pins in {channel_to_archive.mention}"
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
        
        start_message = f"Attempting to remove all pinned messages from {channel_to_unpin.mention}."
        await ctx.send(content=start_message)
        if(channel_to_unpin == None):
            await ctx.send(BOT_ERROR.INACCESSIBLE_CHANNEL)
            return
        pins_to_remove = await channel_to_unpin.pins()
        for pin in pins_to_remove:
            await pin.unpin()
        end_message = f"All pinned messages removed from {channel_to_unpin.mention}."
        await ctx.send(content=end_message)

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
                    line_tokens = line.split(" ")
                    line_tokens = [i for i in line_tokens if i] # remove empty strings for quality of life (doesn't break with extra spaces)
                    for (idx, token) in enumerate(line_tokens):
                        if token == "for" and idx > 0 and line_tokens[idx-1] == str(emoji):
                            role_id = line_tokens[idx+1][3:-1]
                            role = guild.get_role(int(role_id))
                            if payload.event_type == "REACTION_ADD":
                                await user.add_roles(role)
                            else:
                                await user.remove_roles(role)
                            return

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
