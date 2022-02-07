import discord
from discord.ext import commands
import logging
from config import bot as bot_config

# logging conf
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# bot init
bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"),
                   help_command=None,
                   case_insensitive=True,
                   activity=discord.Game("Waiting"),
                   intents=discord.Intents.all()
                   )

bot.load_extension("cog.RoleChecker")
# bot.load_extension("cog.ErrorHandler")

bot.run(bot_config.TOKEN)
