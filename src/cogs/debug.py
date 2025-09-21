import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog

import logging
from utils.portal import Portal
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_big
from utils.logger.decorator import log_command_execution

class Debug_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.debug"))

    @app_commands.command(name = "debug", description = "Provides debug informations about the bot, useful for troubleshooting")
    @log_command_execution
    async def debug(self, ctx:discord.Interaction):
        portal:Portal = Portal.instance()
        embed = discord.Embed(title="Debug Information")

        embed.add_field(name="Version",
                        value=ctx.client.VERSION,
                        inline=True)
        embed.add_field(name="Uptime",
                        value=f"{get_elapsed_time_big(datetime.now().timestamp() - portal.STARTUP_TIMESTAMP)}",
                        inline=True)
        embed.add_field(name="Bot Owner",
                        value=f"<@{portal.bot_config['DISCORD']['OWNER_ID']}>",
                        inline=True)
        embed.add_field(name="Latency to Gateway",
                        value=f"{round(self.__bot.latency * 1000, 2)}ms",
                        inline=True)
        embed.add_field(name="Application ID",
                        value=f"{self.__bot.application_id}",
                        inline=True)
        embed.add_field(name="Number of Guilds",
                        value=f"{len(self.__bot.guilds)}",
                        inline=True)
        embed.add_field(name = "Number of executed commands", value=f"Total: {portal.no_executed_commands}\nSucceeded: {portal.no_succeeded_commands}\nFailed: {portal.no_failed_commands}")

        await ctx.response.send_message(embed=embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(Debug_Command(bot))