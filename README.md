#SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library

##Instructions: 

###Installation and Dependencies:

To add this bot to your Discord server, first ensure you have [Python version 3.5 or later installed](https://www.python.org/downloads/), along with [the discord.py library](https://github.com/Rapptz/discord.py) and [the configobj library](htpps://www.voidspace.org.uk/python/configobj.html#downloading). The asyncio, logging, os.path, and randomlibraries are also required, but they should be included in most Python installations by default. 

Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token). Then, open the santa-bot.py file with your favorite plaintext editor, and replace the word 'token' in the last line that reads `client.run('token')` with the token you have generated, keeping the single quotes. The santa-bot.py file can now be excecuted, and the bot should function as normal.

###Bot Commands:

- `$$join` adds you to the list of secret santa participants.
- `$$setaddress` saves your mailing address for gifts to be sent to.
- `$$setprefs` saves your gift preferences so your secret santa will know what kind of things you would like to receive. Keep in mind that your exact input is sent to your secret santa as is. 
- `$$listparticipants` makes the bot list all of the people currently participating in the secret santa exchange.
- `$$totalparticipants` makes the bot give the number of people currently participating in the secret santa exchange
- *`$$start` to have the bot assign each participant a partner
- *`$$shutdown` to make the bot self-terminate

all commands marked with a * can only be run by a server admin.