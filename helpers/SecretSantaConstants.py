from enum import IntEnum

class SecretSantaConstants(IntEnum):
    """Constants for indexing into each Secret Santa participant's field when parsing the .cfg file"""
    NAME = 0
    DISCRIMINATOR = 1
    IDSTR = 2
    USRNUM = 3
    WISHLISTURL = 4
    PREFERENCES = 5
    PARTNERID = 6
