from discord.ext import commands
import CONFIG

class SantaMiscellaneous(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.command() ### normally commented out because this bot is not meant to be sharded
    async def invite(self, ctx: commands.Context):
        '''
        Creates an invite for this bot
        '''
        link = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=67185664".format(CONFIG.client_id)
        await ctx.send_message("Bot invite link: {0}".format(link))

    @commands.command()
    async def echo(self, ctx: commands.Context, *, content:str):
        '''
        [content] = echos back the [content]
        '''
        await ctx.send(content)

    @commands.command()
    async def ding(self, ctx: commands.Context):
        await ctx.send("dong")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        '''
        = Basic ping command
        '''
        latency = self.bot.latency
        await ctx.send("{0} milliseconds".format(round(latency, 4)*1000))
