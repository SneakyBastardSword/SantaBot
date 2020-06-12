# SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library + some other admin-type stuff for my server

- This bot code must be forked/pulled and run locally
- If you don't want the admin-type stuff, just go in and comment out the add_cog(SantaAdministrative(...)) line

### Requirements
- python 3.5.3 or later (can be installed [here](https://www.python.org/downloads/))
- pip3

### Steps to run:
1. Run `pip3 install -r requirements.txt`
2. Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
3. Replace variables in CONFIG.py
  3a.  Replace `discord_token` and `client_id` in CONFIG.py with your bot token - these two are REQUIRED for all functionality and for the bot to even start
  3b. Replace other variables as you want
      - `role_channel` is REQUIRED for using reaction roles - but will throw an error if unassigned
      - `bot_folder` this is where the .cfg for the Secret Santa participants, the debug log, and the SQLite database files are stored
      - `prefix` change it to whatever you want otherwise commands default to YOUR_PREFIX_HEREjoin, YOUR_PREFIX_HEREunpin_all, etc.
      - `cfg_name`, `dbg_name`, `sqlite_name` don't *need* to do anything here unless you want to
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
- `s!assign_role_channel CHANNEL` **(admin only)** = change the channel the bot looks at for reaction roles
- `s!archive pins SRC_CHANNEL DEST_CHANNEL` **(admin only)** = archive all pins from the source channel to the destination channel as messages
- `s!unpin_all [CHANNEL_ID]` **(admin only)** = unpin all messages in the indicated channel (defaults to the channel the command is called in)

#### Utility Commands:
- `s!emote [any number of emotes]` = returns the URL of the emote image/gif for convenience
- `s![countdown|cd]` = set/check a countdown (global for the server, e.g. time until a Manga Club event) - help text is returns as needed

#### Miscellaneous Commands:

- `s!ping` = check if bot is alive
- `s!echo` = make the bot say stuff
- `s!ding` = dong
