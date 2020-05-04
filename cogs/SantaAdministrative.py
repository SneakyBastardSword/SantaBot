import CONFIG

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument
from discord import RawReactionActionEvent

import helpers.BOT_ERROR as BOT_ERROR

class SantaAdministrative(commands.Cog, name='Administrative'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_channel = CONFIG.role_channel

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def assign_role_channel(self, ctx: commands.Context, reaction_role_channel: int):
        '''
        Not recommended. Allows a reaction role channel to be assigned.
        The recommended route is to set the role_channel variable in the bot's config file to the channel ID you want.
        '''
        dest_channel = self.bot.get_channel(reaction_role_channel)
        self.ROLE_CHANNEL = reaction_role_channel
        if dest_channel != None:
            await ctx.send(content="Reaction role channel assigned to <#{0}>".format(self.ROLE_CHANNEL))
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
        src_channel = self.bot.get_channel(src_id)
        dest_channel = self.bot.get_channel(dest_id)
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
        
        remove_channel = self.bot.get_channel(channel_id_to_unpin)
        start_message = "Attempting to remove all pinned messages from <#{0}>.".format(channel_id_to_unpin)
        await ctx.send(content=start_message)
        pins_to_remove = await remove_channel.pins()
        for pin in pins_to_remove:
            await pin.unpin()
        end_message = "All pinned messages removed from <#{0}>.".format(channel_id_to_unpin)
        await ctx.send(content=end_message)

    @unpin_all.error
    @archive_pins.error
    async def pin_archive_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = BOT_ERROR.NO_PERMISSION("mod")
            await ctx.send(content=text)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(content=BOT_ERROR.MISSING_ARGUMENTS)
        else:
            await ctx.send(content="Error: undetermined please contact <@224949031514800128>")

    @commands.Cog.listener(name='on_raw_reaction_add')
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def manage_reactions(self, payload: RawReactionActionEvent):
        if(self.ROLE_CHANNEL == -1):
            print(BOT_ERROR.REACTION_ROLE_UNASSIGNED)
            return

        message_id = payload.message_id
        channel_id = payload.channel_id
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
    
        if channel_id == self.ROLE_CHANNEL:
            channel = self.bot.get_channel(self.ROLE_CHANNEL)
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
                            print(payload.event_type)
                            if payload.event_type == "REACTION_ADD":
                                await user.add_roles(role)
                            else:
                                await user.remove_roles(role)
