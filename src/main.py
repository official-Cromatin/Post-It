from datetime import datetime
startup = datetime.now().timestamp()

# Initialize the logger
from utils.logger.custom_logging import Custom_Logger
Custom_Logger.initialize()

import logging
app_logger = logging.getLogger("app")

from utils.adv_configparser import Advanced_ConfigParser
from utils.datetime_tools import get_elapsed_time_smal, get_elapsed_time_big
import discord
from discord.ext import commands
from pathlib import Path
import re
import sys
import traceback
from utils.portal import Portal

source_path = Path(__file__).resolve()
base_path = source_path.parents[1]
app_logger.info(f"Using the following path as entrypoint: '{base_path}'")

intents = discord.Intents.default()
intents.messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, help_command=None, intents=intents)

    async def setup_hook(self):
        # Register cogs to handle commands
        for cog_name in ["about", "reload"]:
            await self.load_extension(f"cogs.{cog_name}")
        await self.tree.sync()

bot = MyBot()
bot_config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "bot.ini"))
if re.match(r'[A-Za-z\d]{24}\.[\w-]{6}\.[\w-]{27}', bot_config["DISCORD"]["TOKEN"]):
    app_logger.critical("Bot (config/bot.ini) configuration invalid, please set a valid token")
    quit(1)
elif bot_config.compare_to_template() not in ("equal", "config_minus"):
    app_logger.critical("Bot (config/bot.ini) configuration is missing some parts. Make sure it at least has all the same keys as the template")
    quit(1)
else:
    app_logger.info("Bot configuration valid, continuing with startup")

@bot.event
async def on_ready():
    app_logger.info(f"Successfully logged in (after {get_elapsed_time_smal(datetime.now().timestamp() - startup)}) as {bot.user}")

@bot.tree.error
async def on_app_command_error(ctx, error):
    # Traceback für mehr Informationen zum Fehler
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__)

# Execute some housekeeping actions
portal = Portal.instance()
portal.bot_config = bot_config

try:
    bot.run(bot_config["DISCORD"]["TOKEN"], log_handler = None)
except discord.errors.LoginFailure:
    app_logger.critical("Improper token has been passed. Aborting startup")
    quit(1)

app_logger.info("Quitting application ...")
asyncio.run(bot.close())
app_logger.info(f"Exiting. Application ran for {get_elapsed_time_big(datetime.now().timestamp() - startup)}")