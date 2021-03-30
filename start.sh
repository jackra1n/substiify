#!/bin/bash

# start bot in a new screen

screen -dmS discord-bot python3 bot.py
screen -t discord-bot -X multiuser on