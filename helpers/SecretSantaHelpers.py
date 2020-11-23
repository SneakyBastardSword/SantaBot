import copy
import random
from discord import Member
from discord.abc import PrivateChannel
import discord
from helpers.SecretSantaParticipant import SecretSantaParticipant

class SecretSantaHelpers():

    def isListOfParticipants(self, usrlist: list):
        for usr in usrlist:
            if(not isinstance(usr, SecretSantaParticipant)):
                return False

    def user_is_participant(self, usrid: discord.User.id, usrlist: list):
        """Takes a discord user ID string and returns whether
        a user with that ID is in usr_list"""
        print(usrlist)
        for person in usrlist:
            if int(person.idstr) == usrid:
                return True
        return False

    def get_participant_object(self, usrid: int, usrlist: list):
        """takes a discord user ID string and list of
        participant objects, and returns the first
        participant object with matching id."""
        for (index, person) in enumerate(usrlist):
            if(int(person.idstr) == usrid):
                return (index, person)
        return (-1, None)

    def propose_partner_list(self, usrlist: list):
        """Generate a proposed partner list"""
        usr_list_copy = copy.deepcopy(usrlist)
        partners = copy.deepcopy(usrlist)
        ## propose partner list
        for user in usr_list_copy:
            candidates = partners
            partner = candidates[random.randint(0, len(candidates) - 1)]
            while(partner.idstr == user.idstr):
                partner = candidates[random.randint(0, len(candidates) - 1)]
                if((len(candidates) == 1) & (candidates[0].idstr == user.idstr)):
                    break # no choice but to pick yourself (this will be declared invalid later)
            #remove user's partner from list of possible partners
            partners.remove(partner)
            #save the partner id to the participant's class instance
            user.partnerid = partner.idstr
        return usr_list_copy

    ## everybody has a partner, nobody's partnered with themselves
    def partners_are_valid(self, usrlist: list):
        """Make sure that everybody has a partner
        and nobody is partnered with themselves"""
        if(not usrlist):
            return False
        result = True
        for user in usrlist:
            result = result & (user.partnerid != '') & (user.partnerid != user.idstr)
        return result

    ## checks if the user list changed during a pause
    def usr_list_changed_during_pause(self, usrlist: list, usr_left: bool):
        """checks if the user list changed during a pause"""
        if(usr_left):# there's probably a better boolean logic way but this is easy
            usr_left = False # acknowledge
            return True

        has_changed = True
        for user in usrlist:
            has_match = (not (str(user.partnerid) == ""))
            has_changed = has_changed & has_match # figures out if all users have a match
        has_changed = has_changed & (not usr_left)
        return (not has_changed) ## if not all users have a match

    def channelIsPrivate(self, channel):
        return isinstance(channel, PrivateChannel)

    def member_is_mod(self, person: discord.Member, mod_list: list):
        """Checks that a given member is in the mod list
        @param person the Member in question"""
        if(isinstance(person, Member)):
            person_roles = person.roles
            person_roles_ids = []
            for person_role in person_roles:
                person_roles_ids.append(person_role.id)
            lst3 = [value for value in person_roles_ids if value in mod_list]
            if(lst3):
                return True
        return False

    def is_role_in_server(self, p_role: str, server_role_hierarchy: list):
        if(isinstance(p_role, str)):
            for server_role in server_role_hierarchy:
                if((str(server_role) == p_role) or (str(server_role.mention) == p_role)):
                    return server_role
        return False
