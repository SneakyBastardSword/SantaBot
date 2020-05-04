# SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library

### Requirements
- python 3.5.3 or later (can be installed [here](https://www.python.org/downloads/))
- pip3

### Steps to run:
1. Run `pip3 install -r requirements.txt`
2. Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
3. Replace `discord_token` and `client_id` in CONFIG.py with your bot token - these two are REQUIRED for all functionality and for the bot to even start
  3a. Replace other variables in CONFIG.py as you want
      - `role_channel` is necessary for using reaction roles
      - `bot_folder` this is where the .cfg file for the Secret Santa participants and the debug log are stored
      - `prefix` change it to whatever you want otherwise commands default to YOUR_PREFIX_HEREjoin, YOUR_PREFIX_HEREunpin_all, etc.
      - `cfg_path` and `dbg_path` don't need to do anything here
4. Run `python3 santa-bot.py`

#### Secret Santa Commands:

- `s!join` = join the Secret Santa
- `s!leave` = leave the Secret Santa
- `s!setwishlisturl [wishlist URL]` = set your wishlist URL (replaces current). You may also add your mailing address. __This field required__.
- `s!getwishlisturl` = bot will PM you your current wishlist
- `s!setprefs [specific preferences, the things you like]` = set preferences (replaces current). Put N/A if none. __This field required__.
- `s!getprefs` = bot will PM you your current preferences
- `s!listparticipants` **(admin only)** = get the current participants
- `s!totalparticipants` = get the total number of participants
- `s!partnerinfo` = be DM'd your partner's information
- `s!start` **(admin only)** = assign Secret Santa partners
- `s!restart` **(admin only)** = attempt to restart Secret Santa after pause without changing partners
- `s!pause` **(admin only)** = pause Secret Santa (will require `s!start` and will reshuffle partners)
- `s!end` **(admin only)** = end Secret Santa

#### Administrative Commands:
- `s!assign_role_channel CHANNEL_ID` **(admin only)** = change the channel the bot looks at for reaction roles
- `s!archive pins SRC_CHANNEL_ID DEST_CHANNEL_ID` **(admin only)** = archive all pins from the source channel to the destination channel as messages
- `s!unpin_all [CHANNEL_ID]` **(admin only)** = unpin all messages in the indicated channel (defaults to the channel the command is called in)

#### Miscellaneous Commands:

- `s!ping` = check if bot is alive
- `s!echo` = make the bot say stuff
- `s!ding` = dong
