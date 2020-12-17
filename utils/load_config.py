import os
import json

## Read config file
config = None
with open('./config.json') as cfg:
    config = json.load(cfg)

TOKEN = config['token']
GUILD = config['guild']
COMMANDS_PREFIX = config['token']
COMMANDS_RIOT_KEY = config['token']
QUOTE_AUTHORS_ID = config['quote_authors_id']
