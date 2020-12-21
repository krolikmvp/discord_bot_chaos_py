import os
import json
import logging
lcfg_logging = logging.getLogger('chaos_logger')
## Read config file
config = None
try:
    with open('./config.json') as cfg:
        config = json.load(cfg)
    lcfg_logging.info("Config loaded")
except Exception:
    lcfg_logging.error("Could not open config file")

TOKEN = config['token']
GUILD = config['guild']
COMMANDS_PREFIX = config['prefix']
COMMANDS_RIOT_KEY = config['riot_key']
QUOTE_AUTHORS_NAMES = config['quote_authors_names']
DATABASE_NAME = config['database_name']
OWNER_ID = config['owner']
ADMINS = config['admins']
RANDOM_QUOTE_CUSTOM_NAME = config['random_quote_command_name']
