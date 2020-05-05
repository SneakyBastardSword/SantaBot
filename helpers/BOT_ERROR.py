ALREADY_JOINED = "`ERROR: You have already joined.`"
DM_FAILED = " `ERROR: DM with information failed to send. Please turn on server DMs to receive important Secret Santa-related messages.`"
EXCHANGE_IN_PROGRESS = "`ERROR: The gift exchange is already in progress.`"
EXCHANGE_STARTED_UNJOINED = "`ERROR: The exchange is already in progress. Please contact an admin about pausing the exchange before using s!join.`"
INVALID_INPUT = "`ERROR: invalid input`"
MISSING_ARGUMENTS = "`ERROR: command usage is missing arguments.`"
NOT_ENOUGH_SIGNUPS = "`ERROR: Secret santa not started. Need more people.`"
NOT_PAUSED = "`ERROR: Secret Santa is not paused`"
NOT_STARTED = "`ERROR: partners have not been assigned yet.`"
REACTION_ROLE_UNASSIGNED = "ERROR: no reaction role channel has been assigned"
SIGNUPS_INCOMPLETE = "`ERROR: Signups incomplete. Time for some love through harassment.`"
UNDETERMINED_CONTACT_CODE_OWNER = "ERROR: undetermined please contact <@224949031514800128> for more information" # @mentions me, the maintainer of SantaBot
UNJOINED = "`ERROR: you have not yet joined the Secret Santa exchange. Use s!join to join the exchange.`"
UNREACHABLE = "`ERROR: this shouldn't happen`"

def ARCHIVE_ERROR_LENGTH(msg_url):
    return "`ERROR: output message is too long pinned message {0} was not archived.`".format(msg_url)
def HAS_NOT_SUBMITTED(usrname):
    return "`ERROR: " + usrname + " has not submitted either a mailing wishlist URL or gift preferences.`"
def NO_PERMISSION(role):
    return "`ERROR: you do not have permissions to do this.\nYou need the {0} role for that.`".format(role)
