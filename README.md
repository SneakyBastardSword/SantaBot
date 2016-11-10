#SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library

##Instructions: 

###Installation and Dependencies:

To add this bot to your Discord server, first ensure you have [Python version 3.5 or later installed](https://www.python.org/downloads/), along with [the discord.py library](https://github.com/Rapptz/discord.py). The asyncio, logging, os.path, random and configparser libraries are also required, but they should be included in most Python installations by default. 

Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token). Then, open the santa-bot.py file with your favorite plaintext editor, and replace the word 'token' in the last line that reads `client.run('token')` with the token you have generated, keeping the single quotes. The santa-bot.py file can now be excecuted, and the bot should function as normal.

###Bot Commands:

- Use `$$join` to add yourself to the list of secret santa participants.
- use `$$setaddress` to set your mailing address for gifts to be sent to.
- Use `$$setprefs` to let your secret santa know what kind of things you would like to receive. Keep in mind that your exact input is sent to your secret santa as is. 
- An admin can use `$$start` to have the bot assign each participant a partner
- An admin can use `$$shutdown` to make the bot self-terminate