import logging

from . import bot

# GetLogger
logger = logging.getLogger("LinkerBot")

# StreamHandler
_sh = logging.StreamHandler()
_sh.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
logger.addHandler(_sh)
del _sh

if bot.DEVMODE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
