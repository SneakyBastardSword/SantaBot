DM_FAILED = " `Error: DM with information failed to send. Please turn on server DMs to receive important Secret Santa-related messages.`"
UNJOINED = "`Error: you have not yet joined the Secret Santa exchange. Use s!join to join the exchange.`"
EXCHANGE_STARTED_UNJOINED = "`Error: The exchange is already in progress. Please contact an admin about pausing the exchange before using s!join.`"
INVALID_INPUT = "`Error: invalid input`"
EXCHANGE_IN_PROGRESS = "`Error: The gift exchange is already in progress.`"
NOT_STARTED = "`Error: partners have not been assigned yet.`"
def NO_PERMISSION(role):
    return "`Error: you do not have permissions to do this.\nYou need the {0} role for that.`".format(role)
ALREADY_JOINED = "`Error: You have already joined.`"
SIGNUPS_INCOMPLETE = "`Error: Signups incomplete. Time for some love through harassment.`"
NOT_PAUSED = "`Error: Secret Santa is not paused`"
def HAS_NOT_SUBMITTED(usrname):
    return "`Error: " + usrname + " has not submitted either a mailing wishlist URL or gift preferences.`"
UNREACHABLE = "`Error: this shouldn't happen`"
NOT_ENOUGH_SIGNUPS = "`Error: Secret santa not started. Need more people.`"
