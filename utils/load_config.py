import os
import json
import logging

## Read config file
config = None
try:
    with open('./config.json') as cfg:
        config = json.load(cfg)
except Exception:
    logging.error("Could not open config file")

TOKEN = config['token']
GUILD = config['guild']
COMMANDS_PREFIX = config['prefix']
COMMANDS_RIOT_KEY = config['riot_key']
QUOTE_AUTHORS_ID = config['quote_authors_id']
DATABASE_NAME = config['database_name']
OWNER_ID = config['owner']
ADMINS = config['admins']
