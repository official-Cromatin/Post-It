"""Contains the BaseCog"""

from discord.ext import commands
import logging

class BaseCog(commands.Cog):
    def __init__(self, bot:commands.Bot, logger:logging.Logger):
        self._bot = bot
        self._logger = logger

    async def cog_load(self):
        self._logger.debug(f"Cog for the '{self.__class__.__name__}' command got loaded")

    async def cog_unload(self):
        self._logger.debug(f"Cog for the '{self.__class__.__name__}' command got unloaded")