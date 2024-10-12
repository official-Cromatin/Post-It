import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog
import logging
from datetime import datetime

class Reload_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.reload"))

    @app_commands.command(name = "reload_all", description = "Reloads all cogs")
    async def about(self, ctx: discord.Interaction):
        self._logger.info("Reloading all cogs ...")
        task_start = datetime.now().timestamp()
        
        cog_names = list(self.__bot.extensions.keys())
        for extension_name in cog_names:
            await self.__bot.reload_extension(extension_name)

        await ctx.response.send_message("Cogs successfully reloaded.")

async def setup(bot:commands.Bot):
    await bot.add_cog(Reload_Command(bot))