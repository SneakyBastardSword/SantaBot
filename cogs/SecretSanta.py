import CONFIG
from configobj import ConfigObj
import os
import copy

from discord.ext import commands

import helpers.BOT_ERROR as BOT_ERROR
from helpers.SecretSantaConstants import SecretSantaConstants
from helpers.SecretSantaHelpers import SecretSantaHelpers
from helpers.SecretSantaParticipant import SecretSantaParticipant

class SecretSanta(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.exchange_started = False
        self.server = ''
        self.usr_list = []
        self.highest_key = 0
        self.user_left_during_pause = False
        self.is_paused = False
        self.SecretSantaHelper = SecretSantaHelpers()
        self.config = None


        #initialize config file
        try:
            self.config = ConfigObj(CONFIG.cfg_path, file_error = True)
        except: 
            try:
                os.mkdir(CONFIG.bot_folder)
            except:
                pass
            self.config = ConfigObj()
            self.config.filename = CONFIG.cfg_path
            self.config['programData'] = {'exchange_started': False}
            self.config['members'] = {}
            self.config.write()

        # retrieve data from config file
        self.exchange_started = self.config['programData'].as_bool('exchange_started')
        for key in self.config['members']:
            data = self.config['members'][str(key)]
            usr = SecretSantaParticipant(data[SecretSantaConstants.NAME], data[SecretSantaConstants.DISCRIMINATOR], data[SecretSantaConstants.IDSTR], data[SecretSantaConstants.USRNUM], data[SecretSantaConstants.WISHLISTURL], data[SecretSantaConstants.PREFERENCES], data[SecretSantaConstants.PARTNERID])
            self.usr_list.append(usr)
            self.highest_key = int(key)

    @bot.command()
    async def setwishlisturl(self, ctx: commands.Context, *destination:str):
        '''
        [Any number of wishlist URLs or mailing addresses] = set wishlist destinations or mailing address. Surround mailing address with quotation marks and separate EACH wishlist destination with a space (eg. amazon.com "P. Sherman 42 Wallaby Way, Sydney" http://rightstufanime.com/).
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list):
            if(self.SecretSantaHelper.channelIsPrivate(ctx.channel)):
                pass
            else:
                await ctx.message.delete()
            (index, user) = self.SecretSantaHelper.get_participant_object(currAuthor.id, self.usr_list)
            new_wishlist = "None"
            if(len(destination) == 0):
                pass
            else:
                new_wishlist = " | ".join(destination)
            try:
                # save to config file
                self.config['members'][str(user.usrnum)][SecretSantaConstants.WISHLISTURL] = new_wishlist
                self.config.write()
                # add the input to the value in the user's class instance
                user.wishlisturl = new_wishlist
                try:
                    await currAuthor.send("New wishlist URL: {0}".format(new_wishlist))
                except:
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            except:
                try:
                    await currAuthor.send(BOT_ERROR.INVALID_INPUT)
                except:
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command()
    async def getwishlisturl(self, ctx: commands.Context):
        '''
        Get current wishlist
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(ctx.author.id, self.usr_list):
            (index, user) = self.SecretSantaHelper.get_participant_object(ctx.author.id, self.usr_list)
            try:
                await currAuthor.send("Current wishlist destination(s): {0}".format(user.wishlisturl))
            except:
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command()
    async def setprefs(self, ctx: commands.Context, *preferences:str):
        '''
        Set new preferences
        '''
        currAuthor = ctx.author
        if self.SantaBotHelper.user_is_participant(currAuthor.id, self.usr_list):
            if(self.SantaBotHelper.channelIsPrivate(ctx.channel)):
                pass
            else:
                await ctx.message.delete()
            (index, user) = self.SantaBotHelper.get_participant_object(currAuthor, self.usr_list)
            new_prefs = "None"
            if(len(preferences) == 0):
                pass
            else:
                new_prefs = " | ".join(preferences)
            try:
                #save to config file
                self.config['members'][str(user.usrnum)][SecretSantaConstants.PREFERENCES] = str(new_prefs)
                self.config.write()
                #add the input to the value in the user's class instance
                user.preferences = new_prefs
                try:
                    await currAuthor.send("New preferences: {0}".format(new_prefs))
                except:
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            except:
                    try:
                        await currAuthor.send(BOT_ERROR.INVALID_INPUT)
                    except:
                        await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    