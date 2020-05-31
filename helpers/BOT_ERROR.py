ALREADY_JOINED = "ERROR: You have already joined."
COUNTDOWN_NAME_TAKEN = "ERROR: That countdown name is already in use."
DM_FAILED = "ERROR: DM with information failed to send. Please turn on server DMs to receive important Secret Santa-related messages."
EXCHANGE_IN_PROGRESS = "ERROR: The gift exchange is already in progress."
EXCHANGE_STARTED_UNJOINED = "ERROR: The exchange is already in progress. Please contact an admin about pausing the exchange before using s!join."
INACCESSIBLE_CHANNEL = "ERROR: the channel specified is not accessible to this bot."
INVALID_INPUT = "ERROR: invalid input."
MISSING_ARGUMENTS = "ERROR: command usage is missing arguments."
NOT_ENOUGH_SIGNUPS = "ERROR: Secret santa not started. Need more people."
NOT_PAUSED = "ERROR: Secret Santa is not paused"
NOT_STARTED = "ERROR: partners have not been assigned yet."
REACTION_ROLE_UNASSIGNED = "ERROR: no reaction role channel has been assigned."
SIGNUPS_INCOMPLETE = "ERROR: Signups incomplete. Time for some love through harassment."
UNDETERMINED_CONTACT_CODE_OWNER = "ERROR: undetermined please contact <@224949031514800128> for more information." # @mentions me, the maintainer of SantaBot
UNJOINED = "ERROR: you have not yet joined the Secret Santa exchange. Use s!join to join the exchange."
UNREACHABLE = "ERROR: this shouldn't happen."

def ARCHIVE_ERROR_LENGTH(msg_url):
    return "ERROR: output message is too long pinned message {0} was not archived.".format(msg_url)
def EXCHANGE_IN_PROGRESS_LEAVE(role):
    return "ERROR: The gift exchange is already in progress. Please contact <@224949031514800128> or {0} about leaving.".format(role)
def HAS_NOT_SUBMITTED(usrname):
    return "ERROR: " + usrname + " has not submitted either a mailing wishlist URL or gift preferences."
def INVALID_COUNTDOWN_COMMAND(attempted_command):
    return "ERROR: invalid countdown option `{0}`.".format(attempted_command)
def INVALID_COUNTDOWN_NAME(cd_name):
    return "ERROR: countdown timer `{0}` does not exist. Use `s!countdown list` to list all countdown timers.".format(cd_name)
def CANNOT_CHANGE_COUNTDOWN(author_name):
    return "ERROR: you do not have permission to change that countdown timer. Please contact {0}".format(author_name)
def NO_PERMISSION(role):
    return "ERROR: you do not have permissions to do this.\nYou need the {0} role for that.".format(role)
