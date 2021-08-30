# DISCONTINUED
This repo has been discontinued due to discord.py not being developed anymore.


# Substiify 
[![CodeFactor](https://www.codefactor.io/repository/github/jackra1n/substiify/badge?s=040f4b69ddabf0ef90b247e1c86bfcd436ab99ba)](https://www.codefactor.io/repository/github/jackra1n/substiify)

### How to run:

There are 2 possibilities to run the bot
1. Docker (prefered by me)
2. `python3 bot.py`

##### Docker:

Build docker image
```bash
docker build -t substiify .
```

Run docker 
`-d`: runs container in the backfround
```bash
docker-compose up -d
```

If you want to see past output of the bot run
```bash
docker logs substiify
```

And finally if you want to see live logs that are being output to shell run
```bash
docker attach substiify
```

You can detach from a container and leave it running using the CTRL-p CTRL-q key sequence.

