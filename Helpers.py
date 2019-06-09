import copy
import random
from Participant import Participant

def user_is_participant(usrid, usrlist):
    """Takes a discord user ID string and returns whether
    a user with that ID is in usr_list"""
    result = False
    for person in usrlist:
        if person.idstr == usrid:
            result = True
            break
    return result

def get_participant_object(usrid, usrlist):
    """takes a discord user ID string and list of
    participant objects, and returns the first
    participant object with matching id."""
    for (index, person) in enumerate(usrlist):
        if person.idstr == usrid:
            return (index, person)

def propose_partner_list(usrlist):
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
def partners_are_valid(usrlist):
    """Make sure that everybody has a partner
    and nobody is partnered with themselves"""
    if(not usrlist):
        return False
    result = True
    for user in usrlist:
        result = result & (user.partnerid != '') & (user.partnerid != user.idstr)
    return result

## checks if the user list changed during a pause
def usr_list_changed_during_pause(usrlist, usr_left):
    if(usr_left):# there's probably a better boolean logic way but this is easy
        usr_left = False # acknowledge
        return True

    has_changed = True
    for user in usrlist:
        has_match = (not (str(user.partnerid) == ""))
        has_changed = has_changed & has_match # figures out if all users have a match
    has_changed = has_changed & (not usr_left)
    return (not has_changed) ## if not all users have a match
