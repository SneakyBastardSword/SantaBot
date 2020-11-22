# SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library + some other admin-type stuff for my server

- This bot code must be pulled (or forked) and run locally
- If you don't want the admin-type stuff, just go in and comment out the add_cog(SantaAdministrative(...)) line

### Requirements
- python 3.6 or later (can be installed [here](https://www.python.org/downloads/))
- pip3

### Steps to run:
1. Run `pip3 install -r requirements.txt`
2. Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
   - **IMPORTANT:** you will need to explicitly enable the Server Members Intent under the Bot tab in the [Discord Application Developer Portal](https://discord.com/developers/applications/) ![as pictured](https://i.imgur.com/mvwTiPE.png)
3. Replace variables in CONFIG.py (I have provided CONFIG.py.example as an example)

   3a. Replace `discord_token` and `client_id` in CONFIG.py with your bot token - these two are REQUIRED for all functionality and for the bot to even start

   3b. Replace other variables as you want

       - `role_channel` is REQUIRED for using reaction roles - will print an error in the console if left as -1

       - `prefix` change it to whatever you want otherwise commands default to YOUR_PREFIX_HEREjoin, YOUR_PREFIX_HEREunpin_all, etc.

       - `bot_folder` this is where the .cfg for the Secret Santa participants, the debug log, and the SQLite database files are stored

       - `cfg_name`, `dbg_name`, `sqlite_name` don't *need* to do anything here unless you want to

       - `min_budget`, `max_budget` are used for the Secret Santa functionality and can be changed depending on what your Discord server agrees upon.
4. Run `python3 santa-bot.py`

### Add a Systemd Service for SantaBot to Autostart on Reboot
To keep SantaBot running even after restart you can create a service.

1. Copy the 'run_santa.sh' to '/usr/local/bin/' directory

- sudo cp run_santa.sh /usr/local/bin/

2. Create a service file or edit the included 'santabot.service' using your favorite text editor and add the default user name to 'User=' and the Group they belong to in 'Group='. To find out what default group a user belongs use 'id -gn usernamehere'

- nano santabot.service

		- [Unit]
		- Description=Santa Discord Bot

		- [Service]
		- User= root
		- Group= root
		- Restart=on-abort
		- WorkingDirectory= "Full Path to Santa Bot Here"
		- ExecStart= /usr/local/bin/run_santa.sh

		- [Install]
		- WantedBy=multi-user.target

3. Copy the santabot.service to '/lib/systemd/system/' 

- sudo cp santabot.service /lib/systemd/system/

4. Enable the service so it will autostart on reboot, then start it.

- sudo systemctl enable santabot.service
- sudo systemctl start santabot.service

5. Then check the status

- sudo systemctl status santabot.service

6. When done using the bot for the season, disable using

- sudo systemctl disable santabot.service

#### FAQ:
1. What if my wishlist URL or preference is multiple words?
   - The bot supports that, just surround it with quotation marks. (e.g. `s!setprefs dog "stuffed rabbit" cat`)
2. Does the wishlist *have* to be a URL? What if one of the Secret Santas prefers sending handmade gifts?
   - No that field is really about having a destination for users to send their gifts. Feel free to use addresses instead of URLs if you so desire. Keep in mind that addresses will need to follow question #1 of this FAQ (e.g. `s!setwishlisturl amazonurl/123 "P Sherman 42 Wallaby Way" rightstufanime`)

#### Secret Santa Commands:

- `s!join` = join the Secret Santa
- `s!leave` = leave the Secret Santa
- `s![setwishlisturl|swlurl] [wishlist URL]` = set your wishlist URL (replaces current). You may also add your mailing address. __wishlist URL is required__.
- `s![getwishlisturl|gwlurl]` = bot will PM you your current wishlist
- `s![setprefs|sprefs] [specific preferences, the things you like]` = set preferences (replaces current). Put N/A if none. __preferences are required__.
- `s![getprefs|gprefs]` = bot will PM you your current preferences
- `s![listparticipants|lp]` **(admin only)** = get the current participants
- `s![totalparticipants|tp]` = get the total number of participants
- `s!partnerinfo` = be DM'd your partner's information
- `s!start` **(admin only)** = assign Secret Santa partners
- `s!restart` **(admin only)** = attempt to restart Secret Santa after pause without changing partners
- `s!pause` **(admin only)** = pause Secret Santa (will require `s!start` and will reshuffle partners)
- `s!end` **(admin only)** = end Secret Santa

#### Administrative Commands:
- `s!assign_role_channel CHANNEL` **(admin only)** = change the channel the bot looks at for reaction roles
- `s!archive_pins SRC_CHANNEL DEST_CHANNEL` **(admin only)** = archive all pins from the source channel to the destination channel as messages (ex. `s!archive_pins #general #archive`)
- `s!unpin_all [CHANNEL_ID]` **(admin only)** = unpin all messages in the indicated channel (defaults to the channel the command is called in)

#### Utility Commands:
- `s!emote [any number of emotes]` = returns the URL of the emote image/gif for convenience
- `s![countdown|cd]` = set/check a countdown (global for the server, e.g. time until a Manga Club event) - help text is returns as needed

#### Miscellaneous Commands:

- `s!ping` = check if bot is alive
- `s!echo` = make the bot say stuff
- `s!ding` = dong
