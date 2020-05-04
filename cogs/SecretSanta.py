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

    def __init__(self, bot : commands.Bot, config: ConfigObj):
        self.bot = bot
        self.exchange_started = False
        self.server = ''
        self.usr_list = []
        self.highest_key = 0
        self.user_left_during_pause = False
        self.is_paused = False
        self.SecretSantaHelper = SecretSantaHelpers()
        self.config = config

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
        if self.self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list):
            if(self.self.SecretSantaHelper.channelIsPrivate(ctx.channel)):
                pass
            else:
                await ctx.message.delete()
            (index, user) = self.self.SecretSantaHelper.get_participant_object(currAuthor, self.usr_list)
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

    @commands.command()
    async def getprefs(self, ctx: commands.Context):
        '''
        Get current preferences
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(ctx.author.id, self.usr_list):
            (index, user) = self.SecretSantaHelper.get_participant_object(ctx.author.id, self.usr_list)
            try:
                await currAuthor.send("Current preference(s): {0}".format(user.preferences))
            except:
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command()
    async def start(self, ctx: commands.Context):
        # TODO: add help menu instruction
        currAuthor = ctx.author
        if(currAuthor.top_role == ctx.guild.roles[-1]):
            # first ensure all users have all info submitted
            all_fields_complete = True
            for user in self.usr_list:
                if(user.wishlisturl_is_set() and user.pref_is_set()):
                    pass
                else:
                    all_fields_complete = False
                    try:
                        await currAuthor.send(BOT_ERROR.HAS_NOT_SUBMITTED(user.name))
                        await ctx.send("`Partner assignment cancelled: participant info incomplete.`")
                    except:
                        await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            
            # select a random partner for each participant if all information is complete and there are enough people to do it
            if(all_fields_complete and (len(self.usr_list) > 1)):
                print("Proposing a partner list")
                potential_list = self.SecretSantaHelper.propose_partner_list(self.usr_list)
                while(not self.SecretSantaHelper.partners_are_valid(potential_list)):
                    print("Proposing a partner list")
                    potential_list = self.SecretSantaHelper.propose_partner_list(self.usr_list)
                # save to config file
                print("Partner assignment successful")
                for user in potential_list:
                    (temp_index, temp_user) = self.SecretSantaHelper.get_participant_object(user.idstr, self.usr_list)
                    (index, partner) = self.SecretSantaHelper.get_participant_object(user.partnerid, potential_list)
                    temp_user.partnerid = user.partnerid
                    self.config['members'][str(user.usrnum)][SecretSantaConstants.PARTNERID] = user.partnerid
                    self.config.write()
                    # tell participants who their partner is
                    this_user = ctx.guild.get_member(int(user.idstr))
                    message_pt1 = str(partner.name) + "#" + str(partner.discriminator) + " is your Secret Santa partner! Mosey on over to their wishlist URL(s) and pick out a gift! Remember to keep it in the $10-20 range.\n"
                    message_pt2 = "Their wishlist(s) can be found here: " + partner.wishlisturl + "\n"
                    message_pt3 = "And their gift preferences can be found here: " + partner.preferences + "\n"
                    message_pt4 = "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *secret* santa, after all!"
                    santa_message = message_pt1 + message_pt2 + message_pt3 + message_pt4
                    try:
                        await this_user.send(santa_message)
                    except:
                        await currAuthor.send("Failed to send message to {0}#{1} about their partner. Harass them to turn on server DMs for Secret Santa stuff.".format(this_user.name, this_user.discriminator))
                
                # mark the exchange as in-progress
                exchange_started = True
                is_paused = False
                self.config['programData']['exchange_started'] = True
                self.config.write()
                usr_list = copy.deepcopy(potential_list)
                await ctx.send("Secret Santa pairs have been picked! Check your PMs and remember not to let your partner know. Have fun!")
            elif not all_fields_complete:
                await ctx.send(currAuthor.mention + BOT_ERROR.SIGNUPS_INCOMPLETE)
            elif not (len(self.usr_list) > 1):
                await ctx.send(BOT_ERROR.NOT_ENOUGH_SIGNUPS)
            else:
                await ctx.send(BOT_ERROR.UNREACHABLE)
        else:
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        return

    @commands.command()
    async def restart(self, ctx: commands.Context):
        # TODO: add help menu instruction
        currAuthor = ctx.author
        is_paused = True
        if((currAuthor.top_role == ctx.guild.roles[-1]) and is_paused):
            # ensure all users have all info submitted
            all_fields_complete = True
            for user in self.usr_list:
                if(user.wishlisturl_is_set() and user.pref_is_set()):
                    pass
                else:
                    all_fields_complete = False
                    try:
                        await currAuthor.send(BOT_ERROR.HAS_NOT_SUBMITTED(user.name))
                        await ctx.send("`Partner assignment cancelled: participant info incomplete.`")
                    except:
                        await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            list_changed = self.SecretSantaHelper.usr_list_changed_during_pause(self.usr_list, self.user_left_during_pause)
            if(list_changed):
                ctx.send("User list changed during the pause. Partners must be picked again with `{0}start`.".format(CONFIG.prefix))
            else:
                exchange_started = True
                is_paused = False
                self.config['programData']['exchange_started'] = True
                self.config.write()
                await ctx.send("No change was made during the pause. Secret Santa resumed with the same partners.")
        elif(currAuthor.top_role != ctx.guild.roles[-1]):
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        elif(not is_paused):
            await ctx.send(BOT_ERROR.NOT_PAUSED)
        else:
            await ctx.send(BOT_ERROR.UNREACHABLE)
        return

    @commands.command()
    async def pause(self, ctx: commands.Context):
        # TODO: add help menu instruction
        if(ctx.author.top_role == ctx.guild.roles[-1]):
            exchange_started = False
            self.config['programData']['exchange_started'] = False
            self.config.write()
            is_paused = True
            await ctx.send("Secret Santa has been paused. New people may now join.")
        else:
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        return

    @commands.command()
    async def join(self, ctx: commands.Context):
        '''
        Join Secret Santa if it has not started. Contact the Secret Santa admin if you wish to join.
        '''
        currAuthor = ctx.author
        # check if the exchange has already started
        if self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list):
            await ctx.send(BOT_ERROR.ALREADY_JOINED)
        else:
            # initialize instance of Participant for the author
            self.highest_key = self.highest_key + 1
            self.usr_list.append(SecretSantaParticipant(currAuthor.name, currAuthor.discriminator, currAuthor.id, self.highest_key))
            # write details of the class instance to config and increment total_users
            self.config['members'][str(self.highest_key)] = [currAuthor.name, currAuthor.discriminator, currAuthor.id, self.highest_key, "", "", ""]
            self.config.write()

            # prompt user about inputting info
            await ctx.send(currAuthor.mention + " has been added to the {0} Secret Santa exchange!".format(str(ctx.guild)) + "\nMore instructions have been DMd to you.")
            try:
                userPrompt = """Welcome to the __{0}__ Secret Santa! Please input your wishlist URL and preferences **(by DMing this bot)** so your Secret Santa can send you something.\n
                    Use `{1}setwishlisturl [wishlist urls separated by a space ]` to set your wishlist URL (you may also add your mailing address).\n
                    Use `{2}setprefs [preferences separated by a space ]` to set gift preferences for your Secret Santa. Put N/A if none.""".format(str(ctx.guild), CONFIG.prefix, CONFIG.prefix)
                await currAuthor.send(userPrompt)
            except:
                ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        return

    @commands.command()
    async def leave(self, ctx: commands.Context):
        # TODO: add help menu instruction
        currAuthor = ctx.author
        if(self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list)):
            (index, user) = self.SecretSantaHelper.get_participant_object(currAuthor.id, self.usr_list)
            self.usr_list.remove(user)
            popped_user = self.config['members'].pop(str(user.usrnum))
            self.config.write()
            if(self.is_paused):
                user_left_during_pause = True
            await ctx.send(currAuthor.mention + " has left the {0} Secret Santa exchange".format(str(ctx.guild)))
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command()
    async def end(self, ctx: commands.Context):
        # TODO: add help menu instruction
        if(ctx.author.top_role == ctx.guild.roles[-1]):
            exchange_started = False
            is_paused = False
            self.config['programData']['exchange_started'] = False
            highest_key = 0
            del self.usr_list[:]
            print(len(self.usr_list))
            self.config['members'].clear()
            self.config.write()
            await ctx.send("Secret Santa ended")
        else:
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        return

    @commands.command()
    async def listparticipants(self, ctx: commands.Context):
        # TODO: add help menu instruction
        if(ctx.author.top_role == ctx.guild.roles[-1]):
            if(self.highest_key == 0):
                await ctx.send("Nobody has signed up for the secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
            else:
                msg = '```The following people are signed up for the Secret Santa exchange:\n'
                for user in self.usr_list:
                    this_user = ctx.guild.get_member(user.idstr)
                    msg = msg + str(user.name) + "#" + str(user.discriminator) + "\n"
                msg = msg + "\nUse `{0}join` to enter the exchange.```".format(CONFIG.prefix)
        else:
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        return

    @commands.command()
    async def totalparticipants(self, ctx: commands.Context):
        # TODO: add help menu instruction
        if self.highest_key == 0:
            await ctx.send("Nobody has signed up for the Secret Santa exchange yet. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
        elif self.highest_key == 1:
            await ctx.send("1 person has signed up for the Secret Santa exchange. Use `{0}join` to enter the exchange.".format(CONFIG.prefix))
        else:
            await ctx.send("{0} people have joined the Secret Santa exchange so far. Use `{1}join` to enter the exchange.".format(str(len(self.usr_list)), CONFIG.prefix))
        return

    @commands.command()
    async def partnerinfo(self, ctx: commands.Context):
        # TODO: add help menu instruction
        currAuthor = ctx.author
        authorIsParticipant = self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list)
        if(self.exchange_started and authorIsParticipant):
            (usr_index, user) = self.SecretSantaHelper.get_participant_object(currAuthor, self.usr_list)
            (partner_index, partnerobj) = self.SecretSantaHelper.get_participant_object(user.partnerid, self.usr_list)
            msg = "Your partner is " + partnerobj.name + "#" + partnerobj.discriminator + "\n"
            msg = msg + "Their wishlist(s) can be found here: " + partnerobj.wishlisturl + "\n"
            msg = msg + "And their gift preferences can be found here: " + partnerobj.preferences + "\n"
            msg = msg + "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *Secret* Santa, after all!"
            try:
                await currAuthor.send(msg)
                await ctx.send("The information has been sent to your DMs.")
            except:
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        elif((not self.exchange_started) and authorIsParticipant):
            await ctx.send(BOT_ERROR.NOT_STARTED)
        elif(self.exchange_started and (not authorIsParticipant)):
            await ctx.send(BOT_ERROR.EXCHANGE_STARTED_UNJOINED)
        elif((not self.exchange_started) and (not authorIsParticipant)):
            await ctx.send(BOT_ERROR.UNJOINED)
        else:
            await ctx.send(BOT_ERROR.UNREACHABLE)
        return