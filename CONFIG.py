import os
import pathlib

discord_token = "YOUR_TOKEN_HERE"
client_id = "YOUR_CLIENT_ID"
prefix = "YOUR_PREFIX_HERE"
bot_folder = "YOUR_STORAGE_FOLDER_NAME_HERE"
cfg_name = "botdata.cfg"
sqlite_name = "santabotdb.sqlite"
dbg_name = "debug.log"
role_channel = -1


###############################################
###           DO NOT CHANGE BELOW           ###
###############################################
cfg_path = os.path.join(str(pathlib.Path(__file__).parent), bot_folder, cfg_name)
sqlite_path = os.path.join(str(pathlib.Path(__file__).parent), bot_folder, sqlite_name)
dbg_path = os.path.join(str(pathlib.Path(__file__).parent), bot_folder, dbg_name)
