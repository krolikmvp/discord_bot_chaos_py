import os
import json
import logging
lcfg_logging = logging.getLogger('chaos_logger')
config_name = './config.json'
config = None
try:
    with open(config_name) as cfg:
        config = json.load(cfg)
    lcfg_logging.info("Config loaded")
except Exception:
    lcfg_logging.error("Could not open config file: {config_name}")
    raise FileNotFoundError("Could not open config file: {config_name}")

try:
    TOKEN = config['token']
except Exception as ex:
    raise KeyError("You need to provide TOKEN to use chaos discord bot")

DATABASE_NAME = config.get('database_name', 'chaos.sqlite')
OWNER_ID = config.get('owner', '')
GUILD = config.get('guild', '')
COMMANDS_PREFIX = config.get('prefix', '==')
COMMANDS_RIOT_KEY = config.get('riot_key', '')
ADMINS = config.get('admins', [])
RANDOM_QUOTE_CUSTOM_NAME = config.get('random_quote_command_name', '')
QUOTE_AUTHORS_NAMES = config.get('quote_authors_names', [])
