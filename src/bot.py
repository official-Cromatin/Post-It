from discord.ext import commands
import discord
from utils.datetime_tools import get_elapsed_time_small, get_elapsed_time_milliseconds
from logging import Logger
from datetime import datetime

class PostIt_Bot(commands.Bot):
    """Class to extend the built-in """
    def __init__(self, startup_time:float, program_version:str, app_logger:Logger):
        intents = discord.Intents.default()
        intents.messages = True
        super().__init__(command_prefix=None, help_command=None, intents=intents)

        self.startup_time = startup_time
        self.PROGRAM_VERSION = program_version
        self.__logger = app_logger

    async def setup_hook(self):
        # # Register cogs to handle commands
        # for cog_name in ["debug", "post"]:
        #     await self.load_extension(f"cogs.{cog_name}")
        # await self.tree.sync()
        pass

    async def on_ready(self):
        self.__logger.info(f"Successfully logged in (after {get_elapsed_time_small(datetime.now().timestamp() - self.startup_time)}) as {self.user}")
