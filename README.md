# SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library

### Requirements
    - python 3.5 or later (can be installed [here](https://www.python.org/downloads/))
    - pip3

### Steps to run:
1. Run `pip3 install -r requirements.txt`
2. Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
3. Replace `discord_token` in CONFIG.py with your bot token
4. Run `python3 santa-bot.py`

#### Bot Commands:

- `s!join` = join the Secret Santa
- `s!leave` = leave the Secret Santa
- `s!setwishlisturl [wishlist URL]` = set your wishlist URL (replaces current). You may also add your mailing address. __This field required__.
- `s!getwishlisturl` = bot will PM you your current wishlist
- `s!setprefs [specific preferences, the things you like]` = set preferences (replaces current). Put N/A if none. __This field required__.
- `s!getprefs` = bot will PM you your current preferences
- `s!listparticipants` = get the current participants
- `s!totalparticipants` = get the total number of participants
- `s!partnerinfo` = be DM'd your partner's information
- `s!start` **(admin only)** = assign Secret Santa partners
- `s!restart` **(admin only)** = attempt to restart Secret Santa after pause without changing partners
- `s!pause` **(admin only)** = pause Secret Santa (will require `s!start` and will reshuffle partners)
- `s!end` **(admin only)** = end Secret Santa
- `s!ping` = check if bot is alive