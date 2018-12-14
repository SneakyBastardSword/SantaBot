#!/bin/bash
### Honestly don't use this unless you KNOW it's not going to fail.
### This script was written because discord.py does not relaunch bots that run into WebSocket errors but the rewrite does.
### This is to get around that.

while true
do
    python3 santa-bot.py
    sleep 10
done