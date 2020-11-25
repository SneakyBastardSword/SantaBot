import CONFIG
from configobj import ConfigObj
import copy
from traceback import print_exc

from discord.ext import commands

import helpers.BOT_ERROR as BOT_ERROR
from helpers.SecretSantaConstants import SecretSantaConstants
from helpers.SecretSantaHelpers import SecretSantaHelpers
from helpers.SecretSantaParticipant import SecretSantaParticipant

class SecretSanta(commands.Cog, name='Secret Santa'):

    def __init__(self, bot: commands.Bot, config: ConfigObj):
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

    @commands.command(aliases=["swlurl"])
    async def setwishlisturl(self, ctx: commands.Context, *destination:str):
        '''
        [Any number of wishlist URLs or mailing addresses] = set wishlist destinations or mailing address. Surround mailing address with quotation marks and separate EACH wishlist destination with a space (eg. amazonurl/123 "Sesame Street" http://rightstufanime.com/).
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
                    await currAuthor.send(f"New wishlist URL(s): {new_wishlist}")
                    if(not user.pref_is_set()):
                        userPrompt = f"Great! Now please specify what your preferences for your wishlist might be. Use `{CONFIG.prefix}setprefs [preferences separated by a space]` (e.g. `{CONFIG.prefix}setprefs hippopotamus \"stuffed rabbit\" dog`). Defaults to N/A if not entered."
                        await currAuthor.send(userPrompt)
                    if(user.wishlisturl_is_set() and user.pref_is_set()):
                        signup_complete_msg = f"Congrats, you're now officially enrolled in the Secret Santa! You may change your wishlist URL or preferences with `{CONFIG.prefix}setwishlisturl` or `{CONFIG.prefix}setprefs` any time before the admin begins the Secret Santa."
                        await currAuthor.send(signup_complete_msg)
                except Exception as e:
                    print_exc(e)
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            except Exception as e:
                print_exc(e)
                try:
                    await currAuthor.send(BOT_ERROR.INVALID_INPUT)
                except Exception as e:
                    print_exc(e)
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command(aliases=["gwlurl"])
    async def getwishlisturl(self, ctx: commands.Context):
        '''
        Get current wishlist
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(ctx.author.id, self.usr_list):
            (index, user) = self.SecretSantaHelper.get_participant_object(ctx.author.id, self.usr_list)
            try:
                await currAuthor.send(f"Current wishlist destination(s): {user.wishlisturl}")
            except Exception as e:
                print_exc(e)
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command(aliases=["sprefs"])
    async def setprefs(self, ctx: commands.Context, *preferences:str):
        '''
        Set new preferences
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list):
            if(self.SecretSantaHelper.channelIsPrivate(ctx.channel)):
                pass
            else:
                await ctx.message.delete()
            (index, user) = self.SecretSantaHelper.get_participant_object(currAuthor.id, self.usr_list)
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
                    await currAuthor.send(f"New preferences: {new_prefs}")
                    if(not user.wishlisturl_is_set()):
                        userPrompt = f"Great! Now please specify what your wishlist URL or mailing address. Use `{CONFIG.prefix}setwishlisturl [wishlist urls separated by a space]` (e.g. `{CONFIG.prefix}setwishlisturl amazonurl/123 \"sesame street\"`) to set your wishlist URL."
                        await currAuthor.send(userPrompt)
                    if(user.wishlisturl_is_set() and user.pref_is_set()):
                        signup_complete_msg = f"Congrats, you're now officially enrolled in the Secret Santa! You may change your wishlist URL or preferences with `{CONFIG.prefix}setwishlisturl` or `{CONFIG.prefix}setprefs` any time before the admin begins the Secret Santa."
                        await currAuthor.send(signup_complete_msg)
                except Exception as e:
                    print_exc(e)
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            except Exception as e:
                print_exc(e)
                try:
                    await currAuthor.send(BOT_ERROR.INVALID_INPUT)
                except Exception as e:
                    print_exc(e)
                    await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.command(aliases=["gprefs"])
    async def getprefs(self, ctx: commands.Context):
        '''
        Get current preferences
        '''
        currAuthor = ctx.author
        if self.SecretSantaHelper.user_is_participant(ctx.author.id, self.usr_list):
            (index, user) = self.SecretSantaHelper.get_participant_object(ctx.author.id, self.usr_list)
            try:
                await currAuthor.send(f"Current preference(s): {user.preferences}")
            except Exception as e:
                print_exc(e)
                await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.guild_only()
    @commands.command()
    async def start(self, ctx: commands.Context):
        '''
        Begin the Secret Santa
        '''
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
                    except Exception as e:
                        print_exc(e)
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
                    (temp_index, temp_user) = self.SecretSantaHelper.get_participant_object(int(user.idstr), self.usr_list)
                    (index, partner) = self.SecretSantaHelper.get_participant_object(user.partnerid, potential_list)
                    temp_user.partnerid = user.partnerid
                    self.config['members'][str(user.usrnum)][SecretSantaConstants.PARTNERID] = user.partnerid
                    self.config.write()
                    # tell participants who their partner is
                    this_user = ctx.guild.get_member(int(user.idstr))
                    message_pt1 = f"{str(partner.name)}#{str(partner.discriminator)} is your Secret Santa partner! Mosey on over to their wishlist URL(s) and pick out a gift! Remember to keep it in the ${CONFIG.min_budget}-{CONFIG.max_budget} range.\n"
                    message_pt2 = f"Their wishlist(s) can be found here: {partner.wishlisturl}\n"
                    message_pt3 = f"And their gift preferences can be found here: {partner.preferences}\n"
                    message_pt4 = "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *secret* santa, after all!"
                    santa_message = message_pt1 + message_pt2 + message_pt3 + message_pt4
                    try:
                        await this_user.send(santa_message)
                    except Exception as e:
                        print_exc(e)
                        await currAuthor.send(f"Failed to send message to {this_user.name}#{this_user.discriminator} about their partner. Harass them to turn on server DMs for Secret Santa stuff.")
                
                # mark the exchange as in-progress
                self.exchange_started = True
                self.is_paused = False
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

    @commands.guild_only()
    @commands.command()
    async def restart(self, ctx: commands.Context):
        '''
        Restart the Secret Santa after pause
        '''
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
                    except Exception as e:
                        print_exc(e)
                        await ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
            list_changed = self.SecretSantaHelper.usr_list_changed_during_pause(self.usr_list, self.user_left_during_pause)
            if(list_changed):
                ctx.send(f"User list changed during the pause. Partners must be picked again with `{CONFIG.prefix}start`.")
            else:
                self.exchange_started = True
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

    @commands.guild_only()
    @commands.command()
    async def pause(self, ctx: commands.Context):
        '''
        Pause for people that want to join last-minute (reshuffles and matches upon restart)
        '''
        if(ctx.author.top_role == ctx.guild.roles[-1]):
            self.exchange_started = False
            self.config['programData']['exchange_started'] = False
            self.config.write()
            self.is_paused = True
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
            self.config['members'][str(self.highest_key)] = [currAuthor.name, currAuthor.discriminator, currAuthor.id, self.highest_key, "", "N/A", ""]
            self.config.write()

            # prompt user about inputting info
            await ctx.send(currAuthor.mention + f" has been added to the {str(ctx.guild)} Secret Santa exchange!" + "\nMore instructions have been DMd to you.")
            try:
                userPrompt = f"Welcome to the __{str(ctx.guild)}__ Secret Santa! To complete your enrollment you'll need to input your wishlist URL and preferences (by DMing this bot) so your Secret Santa can send you something\n"
                await currAuthor.send(userPrompt)
                userPrompt = f".\nFirst we need your wishlist (or the destination for sending gifts). Please use `{CONFIG.prefix}setwishlisturl [wishlist urls separated by a space]` (e.g. `{CONFIG.prefix}setwishlisturl amazonurl/123 \"sesame street\"`) to set your wishlist URL (you may also add your mailing address)."
                await currAuthor.send(userPrompt)
            except Exception as e:
                print_exc(e)
                ctx.send(currAuthor.mention + BOT_ERROR.DM_FAILED)
        return

    @commands.command()
    async def leave(self, ctx: commands.Context):
        '''
        Leave the Secret Santa
        '''
        if(self.exchange_started):
            await ctx.send(BOT_ERROR.EXCHANGE_IN_PROGRESS_LEAVE("a mod"))
            return
        
        currAuthor = ctx.author
        if(self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list)):
            (index, user) = self.SecretSantaHelper.get_participant_object(currAuthor.id, self.usr_list)
            self.usr_list.remove(user)
            popped_user = self.config['members'].pop(str(user.usrnum))
            self.config.write()
            if(self.is_paused):
                self.user_left_during_pause = True
            await ctx.send(currAuthor.mention + f" has left the {str(ctx.guild)} Secret Santa exchange")
        else:
            await ctx.send(BOT_ERROR.UNJOINED)
        return

    @commands.guild_only()
    @commands.command()
    async def end(self, ctx: commands.Context):
        '''
        End the Secret Santa
        '''
        if(ctx.author.top_role == ctx.guild.roles[-1]):
            self.exchange_started = False
            self.is_paused = False
            self.config['programData']['exchange_started'] = False
            self.highest_key = 0
            del self.usr_list[:]
            print(len(self.usr_list))
            self.config['members'].clear()
            self.config.write()
            await ctx.send("Secret Santa ended")
        else:
            await ctx.send(BOT_ERROR.NO_PERMISSION(ctx.guild.roles[-1]))
        return

    @commands.command(aliases=["lp"])
    async def listparticipants(self, ctx: commands.Context):
        '''
        List Secret Santa participants
        '''
        if(self.highest_key == 0):
            await ctx.send(f"```Nobody has signed up for the secret Santa exchange yet. Use `{CONFIG.prefix}join` to enter the exchange.```")
        else:
            msg = '```The following people are signed up for the Secret Santa exchange:\n'
            for user in self.usr_list:
                msg = msg + str(user.name) + "#" + str(user.discriminator) + "\n"
            msg = msg + f"\nUse `{CONFIG.prefix}join` to enter the exchange.```"
            await ctx.send(msg)
        return

    @commands.command(aliases=["tp"])
    async def totalparticipants(self, ctx: commands.Context):
        '''
        Find out how many people have joined the Secret Santa
        '''
        if self.highest_key == 0:
            await ctx.send(f"Nobody has signed up for the Secret Santa exchange yet. Use `{CONFIG.prefix}join` to enter the exchange.")
        elif self.highest_key == 1:
            await ctx.send(f"1 person has signed up for the Secret Santa exchange. Use `{CONFIG.prefix}join` to enter the exchange.")
        else:
            await ctx.send(f"{str(len(self.usr_list))} people have joined the Secret Santa exchange so far. Use `{CONFIG.prefix}join` to enter the exchange.")
        return

    @commands.command()
    async def partnerinfo(self, ctx: commands.Context):
        '''
        Get your partner information via DM (partner name, wishlist, gift preference)
        '''
        currAuthor = ctx.author
        authorIsParticipant = self.SecretSantaHelper.user_is_participant(currAuthor.id, self.usr_list)
        if(self.exchange_started and authorIsParticipant):
            (usr_index, user) = self.SecretSantaHelper.get_participant_object(currAuthor.id, self.usr_list)
            (partner_index, partnerobj) = self.SecretSantaHelper.get_participant_object(user.partnerid, self.usr_list)
            msg = "Your partner is " + partnerobj.name + "#" + partnerobj.discriminator + "\n"
            msg = msg + "Their wishlist(s) can be found here: " + partnerobj.wishlisturl + "\n"
            msg = msg + "And their gift preferences can be found here: " + partnerobj.preferences + "\n"
            msg = msg + "If you have trouble accessing your partner's wishlist, please contact an admin to get in touch with your partner. This is a *Secret* Santa, after all!"
            try:
                await currAuthor.send(msg)
                await ctx.send("The information has been sent to your DMs.")
            except Exception as e:
                print_exc(e)
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

    @start.error
    @restart.error
    @pause.error
    @end.error
    async def dm_error(self, ctx: commands.Context, error):
        if(isinstance(error, commands.NoPrivateMessage)):
            await ctx.send(BOT_ERROR.DM_ERROR)
        else:
            await ctx.send(BOT_ERROR.UNDETERMINED_CONTACT_CODE_OWNER)
        return
