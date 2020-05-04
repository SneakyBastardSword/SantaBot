ALREADY_JOINED = "`Error: You have already joined.`"
DM_FAILED = " `Error: DM with information failed to send. Please turn on server DMs to receive important Secret Santa-related messages.`"
EXCHANGE_IN_PROGRESS = "`Error: The gift exchange is already in progress.`"
EXCHANGE_STARTED_UNJOINED = "`Error: The exchange is already in progress. Please contact an admin about pausing the exchange before using s!join.`"
INVALID_INPUT = "`Error: invalid input`"
MISSING_ARGUMENTS = "`Error: command usage is missing arguments.`"
NOT_ENOUGH_SIGNUPS = "`Error: Secret santa not started. Need more people.`"
NOT_PAUSED = "`Error: Secret Santa is not paused`"
NOT_STARTED = "`Error: partners have not been assigned yet.`"
REACTION_ROLE_UNASSIGNED = "ERROR: no reaction role channel has been assigned"
SIGNUPS_INCOMPLETE = "`Error: Signups incomplete. Time for some love through harassment.`"
UNJOINED = "`Error: you have not yet joined the Secret Santa exchange. Use s!join to join the exchange.`"
UNREACHABLE = "`Error: this shouldn't happen`"

def ARCHIVE_ERROR_LENGTH(msg_url):
    return "`ERROR: output message is too long pinned message {0} was not archived.`".format(msg_url)
def HAS_NOT_SUBMITTED(usrname):
    return "`Error: " + usrname + " has not submitted either a mailing wishlist URL or gift preferences.`"
def NO_PERMISSION(role):
    return "`Error: you do not have permissions to do this.\nYou need the {0} role for that.`".format(role)
